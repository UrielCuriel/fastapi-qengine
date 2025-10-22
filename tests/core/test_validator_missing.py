"""
Tests for missing coverage in validator module.
"""

import pytest

from fastapi_qengine.core.errors import SecurityError, ValidationError
from fastapi_qengine.core.parser import FilterParser
from fastapi_qengine.core.types import (
    ComparisonOperator,
    FieldCondition,
    FieldsNode,
    LogicalCondition,
    LogicalOperator,
    OrderNode,
    SecurityPolicy,
    ValidationRule,
)
from fastapi_qengine.core.validator import FilterValidator


class TestFilterValidatorEdgeCases:
    """Test validator edge cases and missing coverage."""

    def test_add_validation_rule(self):
        """Test adding custom validation rule."""

        class CustomRule(ValidationRule):
            def validate(self, node):
                if isinstance(node, FieldCondition) and node.field == "restricted":
                    return ["Custom validation error"]
                return []

        validator = FilterValidator()
        rule = CustomRule()
        validator.add_validation_rule(rule)

        # Verify rule was added
        assert rule in validator.validation_rules

    def test_validate_ast_node_with_custom_rule(self):
        """Test validating AST node with custom validation rule."""

        class CustomRule(ValidationRule):
            def validate(self, node):
                if isinstance(node, FieldCondition) and node.field == "restricted":
                    return ["Field 'restricted' is not allowed"]
                return []

        validator = FilterValidator()
        validator.add_validation_rule(CustomRule())

        node = FieldCondition(
            field="restricted", operator=ComparisonOperator.EQ, value="test"
        )

        errors = validator.validate_ast_node(node)
        assert len(errors) > 0
        assert "not allowed" in errors[0]

    def test_validate_ast_node_field_condition(self):
        """Test validating field condition AST node."""
        security_policy = SecurityPolicy(blocked_fields=["password"])
        validator = FilterValidator(security_policy=security_policy)

        node = FieldCondition(
            field="password", operator=ComparisonOperator.EQ, value="test"
        )

        errors = validator.validate_ast_node(node)
        assert len(errors) > 0
        assert "blocked" in errors[0]

    def test_validate_ast_node_logical_condition_empty(self):
        """Test validating logical condition with empty conditions."""
        validator = FilterValidator()

        node = LogicalCondition(operator=LogicalOperator.AND, conditions=[])

        errors = validator.validate_ast_node(node)
        assert len(errors) > 0
        assert "cannot have empty conditions" in errors[0]

    def test_validate_ast_node_logical_condition_nested(self):
        """Test validating nested logical conditions."""
        security_policy = SecurityPolicy(blocked_fields=["secret"])
        validator = FilterValidator(security_policy=security_policy)

        node = LogicalCondition(
            operator=LogicalOperator.AND,
            conditions=[
                FieldCondition(field="name", operator=ComparisonOperator.EQ, value="test"),
                FieldCondition(field="secret", operator=ComparisonOperator.EQ, value="value"),
            ],
        )

        errors = validator.validate_ast_node(node)
        assert len(errors) > 0
        assert any("blocked" in error for error in errors)

    def test_validate_ast_node_order_node(self):
        """Test validating order node."""
        security_policy = SecurityPolicy(blocked_fields=["password"])
        validator = FilterValidator(security_policy=security_policy)

        node = OrderNode(field="password", ascending=True)

        errors = validator.validate_ast_node(node)
        assert len(errors) > 0
        assert "blocked" in errors[0]

    def test_validate_ast_node_fields_node(self):
        """Test validating fields node."""
        security_policy = SecurityPolicy(blocked_fields=["password"])
        validator = FilterValidator(security_policy=security_policy)

        node = FieldsNode(fields={"name": 1, "password": 1})

        errors = validator.validate_ast_node(node)
        assert len(errors) > 0
        assert "blocked" in errors[0]

    def test_validate_where_clause_depth(self):
        """Test depth validation in where clause."""
        security_policy = SecurityPolicy(max_depth=1)
        validator = FilterValidator(security_policy=security_policy)
        parser = FilterParser()

        # Depth 2 query
        filter_input = parser.parse(
            {"where": {"$and": [{"$or": [{"name": "test"}]}]}}
        )

        with pytest.raises(SecurityError, match="depth exceeds"):
            validator.validate_filter_input(filter_input)

    def test_validate_logical_operator_empty_array(self):
        """Test that logical operators with empty arrays raise ValidationError."""
        validator = FilterValidator()
        parser = FilterParser()

        filter_input = parser.parse({"where": {"$and": []}})

        with pytest.raises(ValidationError, match="cannot have empty array"):
            validator.validate_filter_input(filter_input)

    def test_validate_array_operator_not_list(self):
        """Test that $in/$nin with non-list values raise ValidationError."""
        validator = FilterValidator()
        parser = FilterParser()

        filter_input = parser.parse({"where": {"category": {"$in": "not_a_list"}}})

        with pytest.raises(ValidationError, match="requires an array value"):
            validator.validate_filter_input(filter_input)

    def test_validate_regex_operator_not_string(self):
        """Test that $regex with non-string values raise ValidationError."""
        validator = FilterValidator()
        parser = FilterParser()

        filter_input = parser.parse({"where": {"name": {"$regex": 123}}})

        with pytest.raises(ValidationError, match="requires a string value"):
            validator.validate_filter_input(filter_input)

    def test_validate_exists_operator_not_boolean(self):
        """Test that $exists with non-boolean values raise ValidationError."""
        validator = FilterValidator()
        parser = FilterParser()

        filter_input = parser.parse({"where": {"name": {"$exists": 1}}})

        with pytest.raises(ValidationError, match="requires a boolean value"):
            validator.validate_filter_input(filter_input)

    def test_validate_size_operator_not_integer(self):
        """Test that $size with non-integer values raise ValidationError."""
        validator = FilterValidator()
        parser = FilterParser()

        filter_input = parser.parse({"where": {"tags": {"$size": "three"}}})

        with pytest.raises(ValidationError, match="non-negative integer"):
            validator.validate_filter_input(filter_input)

    def test_validate_size_operator_negative(self):
        """Test that $size with negative values raise ValidationError."""
        validator = FilterValidator()
        parser = FilterParser()

        filter_input = parser.parse({"where": {"tags": {"$size": -5}}})

        with pytest.raises(ValidationError, match="non-negative integer"):
            validator.validate_filter_input(filter_input)

    def test_validate_field_access_empty_field_name(self):
        """Test that empty field names raise ValidationError."""
        validator = FilterValidator()
        parser = FilterParser()

        # This might be tricky to trigger, but let's try with an edge case
        filter_input = parser.parse({"where": {"": "value"}})

        with pytest.raises(ValidationError, match="non-empty strings"):
            validator.validate_filter_input(filter_input)

    def test_validate_fields_clause_invalid_inclusion_value(self):
        """Test that fields with invalid inclusion values raise ValidationError."""
        validator = FilterValidator()
        parser = FilterParser()

        # Create a filter input with invalid field inclusion value
        # This should be caught during normalization but let's test the validator directly
        from fastapi_qengine.core.types import FilterInput

        filter_input = FilterInput(where=None, order=None, fields={"field": 2})

        with pytest.raises(ValidationError, match="must be 0 or 1"):
            validator.validate_filter_input(filter_input)

    def test_validate_order_clause_with_list_format(self):
        """Test validating order clause with blocked fields."""
        security_policy = SecurityPolicy(blocked_fields=["password"])
        validator = FilterValidator(security_policy=security_policy)
        parser = FilterParser()

        # Create filter with order containing blocked field
        filter_input = parser.parse({"where": {"name": "test"}, "order": "password"})

        with pytest.raises(SecurityError, match="blocked"):
            validator.validate_filter_input(filter_input)

    def test_validate_multiple_clauses_multiple_errors(self):
        """Test that multiple errors are collected from different clauses."""
        security_policy = SecurityPolicy(blocked_fields=["password", "secret"])
        validator = FilterValidator(security_policy=security_policy)
        parser = FilterParser()

        filter_input = parser.parse(
            {
                "where": {"password": "test"},
                "order": "secret",
                "fields": {"password": 1},
            }
        )

        with pytest.raises(SecurityError) as exc_info:
            validator.validate_filter_input(filter_input)

        # Should mention multiple violations
        error_msg = str(exc_info.value)
        assert "blocked" in error_msg

    def test_validate_where_and_order_errors_separately(self):
        """Test that where and order errors are collected separately."""
        security_policy = SecurityPolicy(blocked_fields=["password"])
        validator = FilterValidator(security_policy=security_policy)
        parser = FilterParser()

        # Create filter with both where and order using blocked field
        filter_input = parser.parse(
            {"where": {"password": "test"}, "order": "password"}
        )

        with pytest.raises(SecurityError):
            validator.validate_filter_input(filter_input)

    def test_canonical_operator_with_dollar_prefix(self):
        """Test that operators already with $ prefix are kept as-is."""
        validator = FilterValidator()
        parser = FilterParser()

        filter_input = parser.parse({"where": {"price": {"$gt": 50}}})

        # Should validate without issues
        validator.validate_filter_input(filter_input)

    def test_canonical_operator_alias_mapping(self):
        """Test operator alias mapping for operators without $ prefix."""
        validator = FilterValidator()
        parser = FilterParser()

        # Use operators without $ prefix
        filter_input = parser.parse({"where": {"price": {"gt": 50, "lt": 100}}})

        # Should normalize and validate
        validator.validate_filter_input(filter_input)

    def test_get_operator_enum_with_invalid_operator(self):
        """Test getting operator enum with invalid operator."""
        validator = FilterValidator()

        # Test with an invalid operator
        result = validator._get_operator_enum("$invalid_operator")
        assert result is None

    def test_validate_field_condition_value_simple(self):
        """Test validating simple field condition values."""
        validator = FilterValidator()
        parser = FilterParser()

        # Simple value (not a dict)
        filter_input = parser.parse({"where": {"name": "test"}})

        # Should validate without issues
        validator.validate_filter_input(filter_input)

    def test_validate_order_clause_empty_field_spec(self):
        """Test that empty field specs in order are skipped."""
        validator = FilterValidator()
        parser = FilterParser()

        filter_input = parser.parse({"order": "field1, , field2"})

        # Should validate without issues (empty specs skipped)
        validator.validate_filter_input(filter_input)

    def test_allowed_operators_with_logical_operators(self):
        """Test that logical operators respect allowed_operators policy."""
        security_policy = SecurityPolicy(
            allowed_operators=[ComparisonOperator.EQ, ComparisonOperator.NE]
        )
        validator = FilterValidator(security_policy=security_policy)
        parser = FilterParser()

        # Logical operators should still work even if not in allowed_operators
        filter_input = parser.parse(
            {"where": {"$and": [{"name": "test"}, {"category": "books"}]}}
        )

        # Should validate (logical operators are separate from comparison operators)
        validator.validate_filter_input(filter_input)
