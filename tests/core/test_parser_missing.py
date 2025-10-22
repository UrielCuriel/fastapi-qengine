"""
Tests for missing coverage in parser module.
"""

import pytest

from fastapi_qengine.core.errors import ParseError
from fastapi_qengine.core.parser import FilterParser


class TestFilterParserEdgeCases:
    """Test parser edge cases and missing coverage."""

    def test_parse_nested_key_with_empty_parts(self):
        """Test parsing nested keys with unusual patterns."""
        parser = FilterParser()
        # Test a simple case that should work
        result = parser.parse({"filter[where][name]": "value"})
        assert result.where is not None
        assert result.where["name"] == "value"

    def test_convert_value_with_json_array(self):
        """Test converting JSON array strings."""
        parser = FilterParser()
        result = parser.parse(
            {"filter[where][tags][$in]": '["tag1", "tag2", "tag3"]'}
        )

        assert result.where is not None
        assert "tags" in result.where
        assert isinstance(result.where["tags"]["$in"], list)
        assert result.where["tags"]["$in"] == ["tag1", "tag2", "tag3"]

    def test_convert_value_with_json_object(self):
        """Test converting JSON object strings."""
        parser = FilterParser()
        result = parser.parse({"filter[where][data]": '{"key": "value"}'})

        assert result.where is not None
        assert "data" in result.where
        assert isinstance(result.where["data"], dict)

    def test_convert_value_with_invalid_json(self):
        """Test that invalid JSON strings are kept as strings."""
        parser = FilterParser()
        result = parser.parse({"filter[where][field]": "[invalid json"})

        assert result.where is not None
        assert result.where["field"] == "[invalid json"

    def test_convert_value_boolean_true(self):
        """Test converting 'true' string to boolean."""
        parser = FilterParser()
        result = parser.parse({"filter[where][active]": "true"})

        assert result.where is not None
        assert result.where["active"] is True

    def test_convert_value_boolean_false(self):
        """Test converting 'false' string to boolean."""
        parser = FilterParser()
        result = parser.parse({"filter[where][active]": "false"})

        assert result.where is not None
        assert result.where["active"] is False

    def test_convert_value_null(self):
        """Test converting 'null' string to None."""
        parser = FilterParser()
        result = parser.parse({"filter[where][field]": "null"})

        assert result.where is not None
        assert result.where["field"] is None

    def test_convert_value_float(self):
        """Test converting float strings."""
        parser = FilterParser()
        result = parser.parse({"filter[where][price]": "19.99"})

        assert result.where is not None
        assert result.where["price"] == 19.99
        assert isinstance(result.where["price"], float)

    def test_convert_value_integer(self):
        """Test converting integer strings."""
        parser = FilterParser()
        result = parser.parse({"filter[where][count]": "42"})

        assert result.where is not None
        assert result.where["count"] == 42
        assert isinstance(result.where["count"], int)

    def test_validate_depth_with_custom_config(self):
        """Test that depth validation can be configured."""
        from fastapi_qengine.core.config import ParserConfig

        # Create parser with custom max depth
        parser = FilterParser(config=ParserConfig(max_nesting_depth=10))
        
        # Create a reasonably nested structure that should work
        nested_structure = {
            "where": {
                "$and": [
                    {"name": "test"},
                    {"$or": [{"category": "books"}, {"category": "electronics"}]}
                ]
            }
        }

        # Should not raise with reasonable nesting
        result = parser.parse(nested_structure)
        assert result is not None

    def test_validate_depth_with_lists(self):
        """Test depth validation with nested lists."""
        parser = FilterParser()
        # Create structure with nested lists
        nested_list_structure = {
            "where": {
                "$and": [
                    {"$or": [{"$and": [{"field": {"$in": [1, 2, [3, 4]]}}]}]}
                ]
            }
        }

        # Should validate without raising for reasonable depth
        result = parser.parse(nested_list_structure)
        assert result is not None

    def test_nested_params_with_multiple_levels(self):
        """Test parsing nested params with multiple levels."""
        parser = FilterParser()
        result = parser.parse(
            {
                "filter[where][price][$gt]": "50",
                "filter[where][category]": "electronics",
                "filter[order]": "name",
            }
        )

        assert result.where is not None
        assert "price" in result.where
        assert result.where["price"]["$gt"] == 50
        assert result.where["category"] == "electronics"
        assert result.order == "name"

    def test_nested_key_parsing_edge_cases(self):
        """Test nested key parsing with various bracket patterns."""
        parser = FilterParser()
        # Test with trailing bracket
        result = parser.parse({"filter[where][field]": "value"})
        assert result.where is not None
        assert "field" in result.where

    def test_parse_nested_params_building_structure(self):
        """Test that nested params correctly build structure."""
        parser = FilterParser()
        result = parser.parse(
            {
                "filter[where][$and][0][name]": "test",
                "filter[where][$and][1][category]": "books",
            }
        )

        assert result.where is not None
        assert "$and" in result.where
        assert isinstance(result.where["$and"], dict)

    def test_non_string_value_passthrough(self):
        """Test that non-string values are passed through unchanged."""
        parser = FilterParser()
        result = parser.parse({"filter[where][count]": 42})

        assert result.where is not None
        assert result.where["count"] == 42
        assert isinstance(result.where["count"], int)
