"""
Tests for missing coverage in compiler_base module.
"""

import pytest

from fastapi_qengine.core.compiler_base import compile_condition_helper
from fastapi_qengine.core.errors import CompilerError
from fastapi_qengine.core.types import (
    ASTNode,
    ComparisonOperator,
    FieldCondition,
    LogicalCondition,
    LogicalOperator,
)


class MockQueryAdapter:
    """Mock query adapter for testing."""

    def __init__(self):
        self.conditions = []
        self.sorts = []
        self.projection = None

    def add_where_condition(self, condition):
        self.conditions.append(condition)
        return self

    def add_sort(self, field, ascending=True):
        self.sorts.append((field, ascending))
        return self

    def set_projection(self, fields):
        self.projection = fields
        return self

    def build(self):
        return {
            "conditions": self.conditions,
            "sorts": self.sorts,
            "projection": self.projection,
        }


class MockCompiler:
    """Mock compiler for testing."""

    backend_name = "mock"

    def compile_field_condition(self, condition: FieldCondition):
        return {
            "field": condition.field,
            "operator": condition.operator.value,
            "value": condition.value,
        }

    def compile_logical_condition(self, condition: LogicalCondition):
        return {
            "operator": condition.operator.value,
            "conditions": [
                compile_condition_helper(self, cond) for cond in condition.conditions
            ],
        }


class TestCompilerBase:
    """Test compiler base functionality."""

    def test_compile_condition_helper_field_condition(self):
        """Test compile_condition_helper with FieldCondition."""
        compiler = MockCompiler()
        condition = FieldCondition(
            field="name", operator=ComparisonOperator.EQ, value="test"
        )

        result = compile_condition_helper(compiler, condition)

        assert result["field"] == "name"
        assert result["operator"] == "$eq"
        assert result["value"] == "test"

    def test_compile_condition_helper_logical_condition(self):
        """Test compile_condition_helper with LogicalCondition."""
        compiler = MockCompiler()
        condition = LogicalCondition(
            operator=LogicalOperator.AND,
            conditions=[
                FieldCondition(field="name", operator=ComparisonOperator.EQ, value="test"),
                FieldCondition(field="price", operator=ComparisonOperator.GT, value=50),
            ],
        )

        result = compile_condition_helper(compiler, condition)

        assert result["operator"] == "$and"
        assert len(result["conditions"]) == 2
        assert result["conditions"][0]["field"] == "name"
        assert result["conditions"][1]["field"] == "price"

    def test_compile_condition_helper_unknown_type(self):
        """Test compile_condition_helper with unknown condition type."""
        compiler = MockCompiler()

        # Create a mock node that's neither FieldCondition nor LogicalCondition
        class UnknownNode:
            pass

        unknown_node = UnknownNode()

        with pytest.raises(CompilerError, match="Unknown condition type"):
            compile_condition_helper(compiler, unknown_node)

    def test_query_adapter_protocol_methods(self):
        """Test QueryAdapter protocol methods."""
        adapter = MockQueryAdapter()

        # Test add_where_condition
        adapter.add_where_condition({"field": "value"})
        assert len(adapter.conditions) == 1

        # Test add_sort
        adapter.add_sort("name", True)
        assert len(adapter.sorts) == 1
        assert adapter.sorts[0] == ("name", True)

        # Test set_projection
        adapter.set_projection({"field1": 1, "field2": 0})
        assert adapter.projection is not None

        # Test build
        result = adapter.build()
        assert "conditions" in result
        assert "sorts" in result
        assert "projection" in result

    def test_query_adapter_chaining(self):
        """Test that QueryAdapter methods can be chained."""
        adapter = MockQueryAdapter()

        result = (
            adapter.add_where_condition({"field": "value"})
            .add_sort("name", True)
            .set_projection({"field": 1})
        )

        assert result is adapter
        assert len(adapter.conditions) == 1
        assert len(adapter.sorts) == 1
        assert adapter.projection is not None
