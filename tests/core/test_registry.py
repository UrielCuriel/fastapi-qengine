import pytest

from fastapi_qengine.core.errors import RegistryError
from fastapi_qengine.core.registry import OperatorRegistry, operator_registry


class TestOperatorRegistry:
    """Tests for the OperatorRegistry class"""

    @pytest.fixture
    def registry(self):
        """Return a fresh registry instance for each test"""
        return OperatorRegistry()

    @pytest.fixture
    def sample_operator(self):
        """Return a sample operator function"""

        def custom_op(value):
            return value * 2

        return custom_op

    def test_init(self, registry):
        """Test initialization creates empty operators dict"""
        assert registry._operators == {}

    def test_register_operator_basic(self, registry, sample_operator):
        """Test basic operator registration"""
        registry.register_operator("$custom", sample_operator)

        assert "$custom" in registry._operators
        assert registry._operators["$custom"]["implementation"] == sample_operator
        assert registry._operators["$custom"]["backends"] == []

    def test_register_operator_with_backends(self, registry, sample_operator):
        """Test operator registration with specific backends"""
        backends = ["mongodb", "sqlalchemy"]
        registry.register_operator("$custom", sample_operator, backends)

        assert "$custom" in registry._operators
        assert registry._operators["$custom"]["implementation"] == sample_operator
        assert registry._operators["$custom"]["backends"] == backends

    def test_register_operator_invalid_name(self, registry, sample_operator):
        """Test that operator names must start with $"""
        with pytest.raises(RegistryError, match="Operator names must start with"):
            registry.register_operator("custom", sample_operator)

    def test_get_operator_basic(self, registry, sample_operator):
        """Test retrieving a registered operator"""
        registry.register_operator("$custom", sample_operator)

        result = registry.get_operator("$custom")
        assert result == sample_operator

    def test_get_operator_with_backend(self, registry, sample_operator):
        """Test retrieving an operator with backend compatibility check"""
        registry.register_operator("$custom", sample_operator, ["mongodb"])

        # Should work with compatible backend
        result = registry.get_operator("$custom", "mongodb")
        assert result == sample_operator

    def test_get_operator_backend_incompatible(self, registry, sample_operator):
        """Test retrieving an operator with incompatible backend"""
        registry.register_operator("$custom", sample_operator, ["mongodb"])

        with pytest.raises(RegistryError, match="not supported for backend"):
            registry.get_operator("$custom", "sqlalchemy")

    def test_get_operator_not_found(self, registry):
        """Test retrieving a non-existent operator"""
        with pytest.raises(RegistryError, match="Unknown operator"):
            registry.get_operator("$nonexistent")

    def test_is_registered_true(self, registry, sample_operator):
        """Test checking if operator is registered"""
        registry.register_operator("$custom", sample_operator)

        assert registry.is_registered("$custom") is True

    def test_is_registered_false(self, registry):
        """Test checking if non-existent operator is registered"""
        assert registry.is_registered("$nonexistent") is False

    def test_is_registered_with_backend_compatible(self, registry, sample_operator):
        """Test checking if operator is registered for specific backend - compatible case"""
        registry.register_operator("$custom", sample_operator, ["mongodb"])

        assert registry.is_registered("$custom", "mongodb") is True

    def test_is_registered_with_backend_incompatible(self, registry, sample_operator):
        """Test checking if operator is registered for specific backend - incompatible case"""
        registry.register_operator("$custom", sample_operator, ["mongodb"])

        assert registry.is_registered("$custom", "sqlalchemy") is False

    def test_is_registered_with_backend_all_backends(self, registry, sample_operator):
        """Test checking if operator is registered for all backends"""
        registry.register_operator("$custom", sample_operator)  # No specific backends = all backends

        assert registry.is_registered("$custom", "any_backend") is True

    def test_list_operators_empty(self, registry):
        """Test listing operators from empty registry"""
        assert registry.list_operators() == []

    def test_list_operators_with_entries(self, registry, sample_operator):
        """Test listing all operators"""
        registry.register_operator("$custom1", sample_operator)
        registry.register_operator("$custom2", sample_operator)

        operators = registry.list_operators()
        assert sorted(operators) == ["$custom1", "$custom2"]

    def test_list_operators_with_backend(self, registry, sample_operator):
        """Test listing operators for specific backend"""
        registry.register_operator("$custom1", sample_operator, ["mongodb"])
        registry.register_operator("$custom2", sample_operator, ["sqlalchemy"])
        registry.register_operator("$custom3", sample_operator)  # All backends

        operators = registry.list_operators("mongodb")
        assert sorted(operators) == ["$custom1", "$custom3"]

    def test_global_registry_exists(self):
        """Test that the global operator registry is initialized"""
        assert isinstance(operator_registry, OperatorRegistry)


class TestOperatorRegistryIntegration:
    """Integration tests for the OperatorRegistry"""

    def setup_method(self):
        """Clear the global registry before each test"""
        operator_registry._operators = {}

    def test_register_and_use_custom_operator(self):
        """Test registering and using a custom operator"""

        # Define a custom operator
        def custom_length(value):
            return len(value)

        # Register it
        operator_registry.register_operator("$length", custom_length)

        # Use it
        implementation = operator_registry.get_operator("$length")
        result = implementation("hello")

        assert result == 5

    def test_register_backend_specific_operators(self):
        """Test registering and retrieving backend-specific operators"""

        # MongoDB operator
        def mongo_specific_op(value):
            return f"mongo:{value}"

        # SQLAlchemy operator
        def sql_specific_op(value):
            return f"sql:{value}"

        # Register them
        operator_registry.register_operator("$special", mongo_specific_op, ["mongodb"])
        operator_registry.register_operator("$special_sql", sql_specific_op, ["sqlalchemy"])

        # Check availability
        assert operator_registry.is_registered("$special", "mongodb") is True
        assert operator_registry.is_registered("$special", "sqlalchemy") is False
        assert operator_registry.is_registered("$special_sql", "sqlalchemy") is True

        # List backend-specific operators
        mongo_ops = operator_registry.list_operators("mongodb")
        sql_ops = operator_registry.list_operators("sqlalchemy")

        assert "$special" in mongo_ops
        assert "$special" not in sql_ops
        assert "$special_sql" in sql_ops
        assert "$special_sql" not in mongo_ops
