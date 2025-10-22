# pyright: basic
from typing import Callable
from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi import HTTPException, Request

from fastapi_qengine.core.ast import ASTBuilder
from fastapi_qengine.core.config import QEngineConfig
from fastapi_qengine.core.errors import QEngineError
from fastapi_qengine.core.normalizer import FilterNormalizer
from fastapi_qengine.core.optimizer import ASTOptimizer
from fastapi_qengine.core.parser import FilterParser
from fastapi_qengine.core.types import FilterAST
from fastapi_qengine.core.validator import FilterValidator
from fastapi_qengine.dependency import (
    _build_pipeline,  # pyright: ignore[reportPrivateUsage]
    _execute_query_on_engine,  # pyright: ignore[reportPrivateUsage]
    _get_filter_input_from_request,  # pyright: ignore[reportPrivateUsage]
    _handle_processing_error,  # pyright: ignore[reportPrivateUsage]
    create_qe_dependency,
    process_filter_to_ast,
)


@pytest.fixture
def mock_engine() -> Mock:
    engine: Mock = Mock()
    engine.build_query.return_value = {"mock": "query"}  # pyright: ignore[reportAny]
    return engine


@pytest.fixture
def mock_request() -> Mock:
    request: Mock = Mock(spec=Request)
    request.query_params = {}
    return request


class TestBuildPipeline:
    def test_build_pipeline_returns_expected_components(self) -> None:
        result: tuple[
            QEngineConfig,
            FilterParser,
            FilterNormalizer,
            FilterValidator,
            ASTBuilder,
            ASTOptimizer,
        ] = _build_pipeline()
        assert len(result) == 6
        _, parser, normalizer, validator, ast_builder, optimizer = result
        assert parser.__class__.__name__ == "FilterParser"
        assert normalizer.__class__.__name__ == "FilterNormalizer"
        assert validator.__class__.__name__ == "FilterValidator"
        assert ast_builder.__class__.__name__ == "ASTBuilder"
        assert optimizer.__class__.__name__ == "ASTOptimizer"


class TestProcessFilterToAst:
    @patch("fastapi_qengine.dependency._build_pipeline")
    def test_process_filter_to_ast_calls_pipeline_components(self, mock_build) -> None:  # pyright: ignore[reportMissingParameterType, reportUnknownParameterType]
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
        _ = process_filter_to_ast(filter_input={"field": "value"})

        # Verify calls
        mock_parser.parse.assert_called_once()  # pyright: ignore[reportAny]
        mock_normalizer.normalize.assert_called_once()  # pyright: ignore[reportAny]
        mock_validator.validate_filter_input.assert_called_once()  # pyright: ignore[reportAny]
        mock_ast_builder.build.assert_called_once()  # pyright: ignore[reportAny]
        mock_optimizer.optimize.assert_called_once()  # pyright: ignore[reportAny]


class TestExecuteQueryOnEngine:
    def test_execute_query_build_query_method(self, mock_engine) -> None:  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
        ast: FilterAST = FilterAST()
        result: dict[str, object] = _execute_query_on_engine(
            engine=mock_engine, ast=ast
        )  # pyright: ignore[reportUnknownArgumentType]
        mock_engine.build_query.assert_called_once_with(ast)  # pyright: ignore[reportUnknownMemberType]
        assert result == {"mock": "query"}

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
    def test_dependency_no_filter(
        self, mock_execute, mock_get_input, mock_request, mock_engine
    ):  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
        mock_get_input.return_value = None
        mock_execute.return_value = {"empty": "result"}

        # Create dependency and execute it
        dependency: Callable[[Request, str | None], object] = create_qe_dependency(
            engine=mock_engine
        )  # pyright: ignore[reportUnknownArgumentType]
        result: object = dependency(mock_request, None)  # pyright: ignore[reportUnknownArgumentType]

        # Verify correct handling
        mock_get_input.assert_called_once()  # pyright: ignore[reportUnknownMemberType]
        mock_execute.assert_called_once_with(mock_engine, ast=None)  # pyright: ignore[reportUnknownMemberType]
        assert result == {"empty": "result"}

    @patch("fastapi_qengine.dependency._get_filter_input_from_request")
    @patch("fastapi_qengine.dependency.process_filter_to_ast")
    @patch("fastapi_qengine.dependency._execute_query_on_engine")
    def test_dependency_with_filter(
        self,
        mock_execute,
        mock_process,
        mock_get_input,
        mock_request,
        mock_engine,
    ) -> None:
        mock_get_input.return_value = {"field": "value"}
        mock_ast: FilterAST = FilterAST()
        mock_process.return_value = mock_ast
        mock_execute.return_value = {"filtered": "result"}

        # Create dependency and execute it
        dependency: Callable[[Request, str | None], object] = create_qe_dependency(
            mock_engine
        )  # pyright: ignore[reportUnknownArgumentType]
        result: object = dependency(mock_request, None)  # pyright: ignore[reportUnknownArgumentType]

        # Verify correct processing
        mock_get_input.assert_called_once()  # pyright: ignore[reportUnknownMemberType]
        # Instead of checking for exact parameters, just ensure it was called once with the filter
        assert mock_process.call_count == 1  # pyright: ignore[reportUnknownMemberType]
        assert mock_process.call_args[0][0] == {"field": "value"}  # pyright: ignore[reportUnknownMemberType]
        # The config parameter will be a default QEngineConfig instance, so we don't check its exact value
        mock_execute.assert_called_once_with(mock_engine, mock_ast)  # pyright: ignore[reportUnknownMember -> NoneType]  # pyright: ignore[reportUnknownMemberType]
        assert result == {"filtered": "result"}

    @patch("fastapi_qengine.dependency._get_filter_input_from_request")
    @patch("fastapi_qengine.dependency._handle_processing_error")
    def test_dependency_error_handling(
        self, mock_handle_error, mock_get_input, mock_request, mock_engine
    ) -> None:  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
        mock_get_input.side_effect = ValueError("Test error")

        # Create dependency and execute it
        dependency: Callable[[Request, str | None], object] = create_qe_dependency(
            mock_engine
        )  # pyright: ignore[reportUnknownArgumentType]
        dependency(mock_request, None)  # pyright: ignore[reportUnusedCallResult, reportUnknownArgumentType]

        # Verify error was handled
        mock_handle_error.assert_called_once()  # pyright: ignore[reportUnknownMemberType]
        assert isinstance(mock_handle_error.call_args[0][0], ValueError)  # pyright: ignore[reportUnknownMemberType]
