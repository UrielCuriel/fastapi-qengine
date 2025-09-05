from fastapi_qengine.core.errors import QEngineError, UnsupportedOperatorError


class TestUnsupportedOperatorError:
    def test_initialization_with_operator_only(self):
        """Test that UnsupportedOperatorError can be initialized with just an operator."""
        error = UnsupportedOperatorError("$test")
        assert error.operator == "$test"
        assert error.backend is None
        assert str(error) == "Operator '$test' is not supported"

    def test_initialization_with_operator_and_backend(self):
        """Test that UnsupportedOperatorError can be initialized with both operator and backend."""
        error = UnsupportedOperatorError("$test", "mongodb")
        assert error.operator == "$test"
        assert error.backend == "mongodb"
        assert str(error) == "Operator '$test' is not supported for backend 'mongodb'"

    def test_error_message_formatting(self):
        """Test that the error message is properly formatted."""
        error1 = UnsupportedOperatorError("$in")
        assert str(error1) == "Operator '$in' is not supported"

        error2 = UnsupportedOperatorError("$regex", "sql")
        assert str(error2) == "Operator '$regex' is not supported for backend 'sql'"

    def test_inheritance(self):
        """Test that UnsupportedOperatorError inherits from QEngineError."""
        error = UnsupportedOperatorError("$test")
        assert isinstance(error, UnsupportedOperatorError)
        assert isinstance(error, QEngineError)
        assert isinstance(error, Exception)

    def test_properties(self):
        """Test that the exception properties are properly set."""
        operator = "$custom"
        backend = "custom_backend"
        error = UnsupportedOperatorError(operator, backend)

        assert error.operator == operator
        assert error.backend == backend

        # Test with different values
        error2 = UnsupportedOperatorError("$ne", "sqlalchemy")
        assert error2.operator == "$ne"
        assert error2.backend == "sqlalchemy"
