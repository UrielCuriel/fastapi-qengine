"""
Tests for missing coverage in normalizer module.
"""

import pytest

from fastapi_qengine.core.errors import ValidationError
from fastapi_qengine.core.normalizer import FilterNormalizer
from fastapi_qengine.core.types import FilterInput


class TestFilterNormalizerEdgeCases:
    """Test normalizer edge cases and missing coverage."""

    def test_normalize_logical_operator_with_non_list(self):
        """Test that logical operators with non-list values raise ValidationError."""
        normalizer = FilterNormalizer()
        filter_input = FilterInput(where={"$and": "not_a_list"}, order=None, fields=None)

        with pytest.raises(ValidationError, match="requires an array value"):
            normalizer.normalize(filter_input)

    def test_normalize_field_condition_invalid_operator(self):
        """Test that invalid operators raise ValidationError."""
        normalizer = FilterNormalizer()
        filter_input = FilterInput(
            where={"field": {"invalid_op": "value"}}, order=None, fields=None
        )

        with pytest.raises(ValidationError, match="Invalid operator"):
            normalizer.normalize(filter_input)

    def test_normalize_order_dict_with_numeric_keys(self):
        """Test normalizing order dict with numeric string keys."""
        normalizer = FilterNormalizer()
        filter_input = FilterInput(
            where={"name": "test"},
            order={"0": "field1 ASC", "1": "field2 DESC"},
            fields=None,
        )

        result = normalizer.normalize(filter_input)
        assert result.order == "field1 ASC,field2 DESC"

    def test_normalize_order_dict_with_non_numeric_keys(self):
        """Test normalizing order dict with non-numeric keys."""
        normalizer = FilterNormalizer()
        filter_input = FilterInput(
            where={"name": "test"},
            order={"a": "field1 ASC", "b": "field2 DESC"},
            fields=None,
        )

        result = normalizer.normalize(filter_input)
        # Non-numeric keys should still be processed
        assert result.order is not None
        assert "field1 ASC" in result.order
        assert "field2 DESC" in result.order

    def test_normalize_order_dict_with_non_string_value(self):
        """Test that non-string order values raise ValidationError."""
        normalizer = FilterNormalizer()
        filter_input = FilterInput(
            where={"name": "test"}, order={"0": 123}, fields=None
        )

        with pytest.raises(ValidationError, match="must be a string"):
            normalizer.normalize(filter_input)

    def test_normalize_order_list(self):
        """Test normalizing order as list."""
        normalizer = FilterNormalizer()
        filter_input = FilterInput(
            where={"name": "test"},
            order=["field1 ASC", "field2 DESC"],
            fields=None,
        )

        result = normalizer.normalize(filter_input)
        assert result.order == "field1 ASC,field2 DESC"

    def test_normalize_order_string_with_spaces(self):
        """Test normalizing order string with extra spaces."""
        normalizer = FilterNormalizer()
        filter_input = FilterInput(
            where={"name": "test"}, order="  field1 ASC  ", fields=None
        )

        result = normalizer.normalize(filter_input)
        assert result.order == "field1 ASC"

    def test_normalize_fields_with_boolean_true(self):
        """Test normalizing fields with boolean true."""
        normalizer = FilterNormalizer()
        filter_input = FilterInput(
            where={"name": "test"}, order=None, fields={"field1": True, "field2": False}
        )

        result = normalizer.normalize(filter_input)
        assert result.fields is not None
        assert result.fields["field1"] == 1
        assert result.fields["field2"] == 0

    def test_normalize_fields_with_numeric_values(self):
        """Test normalizing fields with numeric values."""
        normalizer = FilterNormalizer()
        filter_input = FilterInput(
            where={"name": "test"}, order=None, fields={"field1": 1.0, "field2": 0.0}
        )

        result = normalizer.normalize(filter_input)
        assert result.fields is not None
        assert result.fields["field1"] == 1
        assert result.fields["field2"] == 0

    def test_normalize_fields_with_invalid_type(self):
        """Test that invalid field inclusion types raise ValidationError."""
        normalizer = FilterNormalizer()
        filter_input = FilterInput(
            where={"name": "test"}, order=None, fields={"field1": "invalid"}
        )

        with pytest.raises(ValidationError, match="must be boolean or number"):
            normalizer.normalize(filter_input)

    def test_normalize_simple_equality_expansion(self):
        """Test that simple equality is expanded to $eq."""
        normalizer = FilterNormalizer()
        filter_input = FilterInput(where={"name": "test"}, order=None, fields=None)

        result = normalizer.normalize(filter_input)
        assert result.where is not None
        assert result.where["name"]["$eq"] == "test"

    def test_normalize_operator_aliases_without_prefix(self):
        """Test normalizing operators without $ prefix."""
        normalizer = FilterNormalizer()
        filter_input = FilterInput(
            where={"price": {"gt": 50, "lt": 100}}, order=None, fields=None
        )

        result = normalizer.normalize(filter_input)
        assert result.where is not None
        assert "$gt" in result.where["price"]
        assert "$lt" in result.where["price"]
        assert result.where["price"]["$gt"] == 50
        assert result.where["price"]["$lt"] == 100

    def test_normalize_logical_operator_aliases(self):
        """Test normalizing logical operators without $ prefix."""
        normalizer = FilterNormalizer()
        filter_input = FilterInput(
            where={"and": [{"name": "test"}, {"category": "books"}]},
            order=None,
            fields=None,
        )

        result = normalizer.normalize(filter_input)
        assert result.where is not None
        assert "$and" in result.where

    def test_normalize_nested_conditions(self):
        """Test normalizing nested conditions."""
        normalizer = FilterNormalizer()
        filter_input = FilterInput(
            where={
                "$and": [
                    {"price": {"$gt": 10}},
                    {"$or": [{"category": "books"}, {"category": "electronics"}]},
                ]
            },
            order=None,
            fields=None,
        )

        result = normalizer.normalize(filter_input)
        assert result.where is not None
        assert "$and" in result.where
        assert isinstance(result.where["$and"], list)

    def test_normalize_non_dict_condition(self):
        """Test that non-dict conditions are returned as-is."""
        normalizer = FilterNormalizer()
        # This tests the _normalize_condition path for non-dict values
        filter_input = FilterInput(where={"field": "simple_value"}, order=None, fields=None)

        result = normalizer.normalize(filter_input)
        assert result.where is not None
        # Should be expanded to $eq
        assert result.where["field"]["$eq"] == "simple_value"

    def test_canon_logical_case_insensitive(self):
        """Test that logical operator canonicalization is case-insensitive."""
        normalizer = FilterNormalizer()
        filter_input = FilterInput(
            where={"AND": [{"name": "test"}]}, order=None, fields=None
        )

        result = normalizer.normalize(filter_input)
        assert result.where is not None
        assert "$and" in result.where

    def test_canon_comparison_case_insensitive(self):
        """Test that comparison operator canonicalization is case-insensitive."""
        normalizer = FilterNormalizer()
        filter_input = FilterInput(
            where={"price": {"GT": 50}}, order=None, fields=None
        )

        result = normalizer.normalize(filter_input)
        assert result.where is not None
        assert "$gt" in result.where["price"]
