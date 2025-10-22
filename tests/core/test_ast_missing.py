"""
Tests for missing coverage in AST module.
"""

import pytest

from fastapi_qengine.core.ast import ASTBuilder
from fastapi_qengine.core.errors import ParseError
from fastapi_qengine.core.types import (
    ComparisonOperator,
    FieldCondition,
    FilterInput,
    LogicalCondition,
    LogicalOperator,
)


class TestASTBuilderEdgeCases:
    """Test AST builder edge cases and missing coverage."""

    def test_empty_condition_error(self):
        """Test that empty conditions raise ParseError."""
        builder = ASTBuilder()
        filter_input = FilterInput(where={}, order=None, fields=None)

        with pytest.raises(ParseError, match="Empty condition"):
            builder.build(filter_input)

    def test_field_name_starting_with_dollar(self):
        """Test that field names starting with $ are rejected."""
        builder = ASTBuilder()
        filter_input = FilterInput(where={"$invalid_field": "value"}, order=None, fields=None)

        with pytest.raises(ParseError, match="cannot start with '\\$'"):
            builder.build(filter_input)

    def test_invalid_operator_without_dollar(self):
        """Test that operators without $ prefix are rejected."""
        builder = ASTBuilder()
        filter_input = FilterInput(
            where={"field": {"invalid_op": "value"}}, order=None, fields=None
        )

        with pytest.raises(ParseError, match="must start with '\\$'"):
            builder.build(filter_input)

    def test_unknown_operator(self):
        """Test that unknown operators raise ParseError."""
        builder = ASTBuilder()
        filter_input = FilterInput(
            where={"field": {"$unknown": "value"}}, order=None, fields=None
        )

        with pytest.raises(ParseError, match="Unknown operator"):
            builder.build(filter_input)

    def test_single_operator_condition(self):
        """Test building condition with single operator."""
        builder = ASTBuilder()
        filter_input = FilterInput(
            where={"price": {"$gt": 50}}, order=None, fields=None
        )

        ast = builder.build(filter_input)
        assert isinstance(ast.where, FieldCondition)
        assert ast.where.field == "price"
        assert ast.where.operator == ComparisonOperator.GT
        assert ast.where.value == 50

    def test_multiple_operators_on_same_field(self):
        """Test building condition with multiple operators on same field."""
        builder = ASTBuilder()
        filter_input = FilterInput(
            where={"price": {"$gt": 10, "$lt": 100}}, order=None, fields=None
        )

        ast = builder.build(filter_input)
        assert isinstance(ast.where, LogicalCondition)
        assert ast.where.operator == LogicalOperator.AND
        assert len(ast.where.conditions) == 2

    def test_empty_order_field_spec(self):
        """Test that empty order field specs are skipped."""
        builder = ASTBuilder()
        filter_input = FilterInput(
            where={"name": "test"}, order="field1,  ,field2", fields=None
        )

        ast = builder.build(filter_input)
        assert len(ast.order) == 2
        assert ast.order[0].field == "field1"
        assert ast.order[1].field == "field2"

    def test_empty_field_name_in_order(self):
        """Test that empty field names in order are skipped."""
        builder = ASTBuilder()
        filter_input = FilterInput(where={"name": "test"}, order=" ", fields=None)

        # Empty order specs are skipped, resulting in empty order list
        ast = builder.build(filter_input)
        assert len(ast.order) == 0

    def test_field_spec_with_spaces(self):
        """Test parsing field spec with explicit ASC/DESC."""
        builder = ASTBuilder()
        filter_input = FilterInput(
            where={"name": "test"}, order="field1 ASC, field2 DESC", fields=None
        )

        ast = builder.build(filter_input)
        assert len(ast.order) == 2
        assert ast.order[0].field == "field1"
        assert ast.order[0].ascending is True
        assert ast.order[1].field == "field2"
        assert ast.order[1].ascending is False

    def test_field_spec_with_minus_prefix(self):
        """Test parsing field spec with minus prefix for descending."""
        builder = ASTBuilder()
        filter_input = FilterInput(where={"name": "test"}, order="-field1", fields=None)

        ast = builder.build(filter_input)
        assert len(ast.order) == 1
        assert ast.order[0].field == "field1"
        assert ast.order[0].ascending is False

    def test_fields_node_with_invalid_values(self):
        """Test that invalid field inclusion values raise ParseError."""
        builder = ASTBuilder()
        filter_input = FilterInput(
            where={"name": "test"}, order=None, fields={"field1": 2}
        )

        with pytest.raises(ParseError, match="must be 0 or 1"):
            builder.build(filter_input)

    def test_logical_operator_not_list(self):
        """Test that logical operators require list values."""
        builder = ASTBuilder()
        filter_input = FilterInput(where={"$and": "invalid"}, order=None, fields=None)

        with pytest.raises(ParseError, match="requires a list value"):
            builder.build(filter_input)

    def test_order_as_list(self):
        """Test order specification as list."""
        builder = ASTBuilder()
        filter_input = FilterInput(
            where={"name": "test"}, order=["field1 ASC", "field2 DESC"], fields=None
        )

        ast = builder.build(filter_input)
        assert len(ast.order) == 2
        assert ast.order[0].field == "field1"
        assert ast.order[0].ascending is True
        assert ast.order[1].field == "field2"
        assert ast.order[1].ascending is False

    def test_flatten_single_item_logical_nested(self):
        """Test flattening of single-item logical conditions."""
        builder = ASTBuilder()
        # Single item in $and should result in LogicalCondition with single item
        filter_input = FilterInput(
            where={"$and": [{"name": "test"}]}, order=None, fields=None
        )

        ast = builder.build(filter_input)
        # Should be a LogicalCondition with single FieldCondition
        assert isinstance(ast.where, LogicalCondition)
        assert len(ast.where.conditions) == 1
        assert isinstance(ast.where.conditions[0], FieldCondition)
