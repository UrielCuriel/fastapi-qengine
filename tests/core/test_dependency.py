from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi import HTTPException, Request

from fastapi_qengine.core.errors import QEngineError
from fastapi_qengine.core.types import FilterAST
from fastapi_qengine.dependency import (
    _build_pipeline,
    _execute_query_on_engine,
    _get_filter_input_from_request,
    _handle_processing_error,
    create_qe_dependency,
    process_filter_to_ast,
)


@pytest.fixture
def mock_engine():
    engine = Mock()
    engine.build_query.return_value = {"mock": "query"}
    return engine


@pytest.fixture
def mock_request():
    request = Mock(spec=Request)
    request.query_params = {}
    return request


class TestBuildPipeline:
    def test_build_pipeline_returns_expected_components(self):
        result = _build_pipeline()
        assert len(result) == 6
        cfg, parser, normalizer, validator, ast_builder, optimizer = result
        assert parser.__class__.__name__ == "FilterParser"
        assert normalizer.__class__.__name__ == "FilterNormalizer"
        assert validator.__class__.__name__ == "FilterValidator"
        assert ast_builder.__class__.__name__ == "ASTBuilder"
        assert optimizer.__class__.__name__ == "ASTOptimizer"


class TestProcessFilterToAst:
    @patch("fastapi_qengine.dependency._build_pipeline")
    def test_process_filter_to_ast_calls_pipeline_components(self, mock_build):
        # Setup mocks
        mock_parser = Mock()
        mock_normalizer = Mock()
        mock_validator = Mock()
        mock_ast_builder = Mock()
        mock_optimizer = Mock()
        mock_build.return_value = (
            None,
            mock_parser,
            mock_normalizer,
            mock_validator,
            mock_ast_builder,
            mock_optimizer,
        )

        # Run function
        process_filter_to_ast({"field": "value"})

        # Verify calls
        mock_parser.parse.assert_called_once()
        mock_normalizer.normalize.assert_called_once()
        mock_validator.validate_filter_input.assert_called_once()
        mock_ast_builder.build.assert_called_once()
        mock_optimizer.optimize.assert_called_once()


class TestExecuteQueryOnEngine:
    def test_execute_query_build_query_method(self, mock_engine):
        ast = FilterAST()
        result = _execute_query_on_engine(mock_engine, ast)
        mock_engine.build_query.assert_called_once_with(ast)
        assert result == {"mock": "query"}

    def test_execute_query_compile_method(self):
        engine = Mock()
        # Create engine that only has compile method, not build_query
        engine.compile = Mock(return_value={"compiled": "query"})
        delattr(engine, "build_query")

        ast = FilterAST()
        result = _execute_query_on_engine(engine, ast)
        engine.compile.assert_called_once_with(ast)
        assert result == {"compiled": "query"}

    def test_execute_query_invalid_engine(self):
        engine = Mock()
        # Remove both required methods to trigger error
        delattr(engine, "build_query")
        delattr(engine, "compile")

        with pytest.raises(HTTPException) as excinfo:
            _execute_query_on_engine(engine, FilterAST())
        assert excinfo.value.status_code == 500


class TestGetFilterInputFromRequest:
    def test_get_filter_param_priority(self):
        request = MagicMock()
        result = _get_filter_input_from_request(request, '{"name": "test"}')
        assert result == '{"name": "test"}'

    def test_get_filter_from_query_params(self):
        request = MagicMock()
        request.query_params = {"filter[name]": "test", "other": "param"}
        result = _get_filter_input_from_request(request, None)
        assert result == {"filter[name]": "test"}

    def test_no_filter_returns_none(self):
        request = MagicMock()
        request.query_params = {"other": "param"}
        result = _get_filter_input_from_request(request, None)
        assert result is None


class TestHandleProcessingError:
    def test_qengine_error_raised_as_400(self):
        error = QEngineError("Invalid filter")
        with pytest.raises(HTTPException) as excinfo:
            _handle_processing_error(error, False)
        assert excinfo.value.status_code == 400
        assert "Invalid filter" in str(excinfo.value.detail)

    def test_other_error_in_debug_mode(self):
        error = ValueError("Unknown error")
        with pytest.raises(HTTPException) as excinfo:
            _handle_processing_error(error, True)
        assert excinfo.value.status_code == 500
        assert "Unknown error" in str(excinfo.value.detail)

    def test_other_error_in_production_mode(self):
        error = ValueError("Should not be visible")
        with pytest.raises(HTTPException) as excinfo:
            _handle_processing_error(error, False)
        assert excinfo.value.status_code == 400
        assert "Should not be visible" not in str(excinfo.value.detail)


class TestCreateQeDependency:
    @patch("fastapi_qengine.dependency._get_filter_input_from_request")
    @patch("fastapi_qengine.dependency._execute_query_on_engine")
    def test_dependency_no_filter(self, mock_execute, mock_get_input, mock_request, mock_engine):
        mock_get_input.return_value = None
        mock_execute.return_value = {"empty": "result"}

        # Create dependency and execute it
        dependency = create_qe_dependency(mock_engine)
        result = dependency(mock_request)

        # Verify correct handling
        mock_get_input.assert_called_once()
        mock_execute.assert_called_once_with(mock_engine, None)
        assert result == {"empty": "result"}

    @patch("fastapi_qengine.dependency._get_filter_input_from_request")
    @patch("fastapi_qengine.dependency.process_filter_to_ast")
    @patch("fastapi_qengine.dependency._execute_query_on_engine")
    def test_dependency_with_filter(self, mock_execute, mock_process, mock_get_input, mock_request, mock_engine):
        mock_get_input.return_value = {"field": "value"}
        mock_ast = FilterAST()
        mock_process.return_value = mock_ast
        mock_execute.return_value = {"filtered": "result"}

        # Create dependency and execute it
        dependency = create_qe_dependency(mock_engine)
        result = dependency(mock_request)

        # Verify correct processing
        mock_get_input.assert_called_once()
        # Instead of checking for exact parameters, just ensure it was called once with the filter
        assert mock_process.call_count == 1
        assert mock_process.call_args[0][0] == {"field": "value"}
        # The config parameter will be a default QEngineConfig instance, so we don't check its exact value
        mock_execute.assert_called_once_with(mock_engine, mock_ast)
        assert result == {"filtered": "result"}

    @patch("fastapi_qengine.dependency._get_filter_input_from_request")
    @patch("fastapi_qengine.dependency._handle_processing_error")
    def test_dependency_error_handling(self, mock_handle_error, mock_get_input, mock_request, mock_engine):
        mock_get_input.side_effect = ValueError("Test error")

        # Create dependency and execute it
        dependency = create_qe_dependency(mock_engine)
        dependency(mock_request)

        # Verify error was handled
        mock_handle_error.assert_called_once()
        assert isinstance(mock_handle_error.call_args[0][0], ValueError)
