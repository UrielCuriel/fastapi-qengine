"""
Test different order format options.
"""

from typing import Any, Dict, List, cast

from fastapi_qengine.core.ast import ASTBuilder
from fastapi_qengine.core.normalizer import FilterNormalizer
from fastapi_qengine.core.parser import FilterParser
from fastapi_qengine.core.types import FilterAST, OrderNode


def process_filter(filter_input: Dict[str, Any]) -> FilterAST:
    """Helper to process filter input through the pipeline."""
    parser = FilterParser()
    normalizer = FilterNormalizer()
    ast_builder = ASTBuilder()

    parsed = parser.parse(filter_input)
    normalized = normalizer.normalize(parsed)
    return ast_builder.build(normalized)


def test_string_order_format():
    """Test the string format for order: "propertyName ASC"."""
    # Test string format with ASC
    ast = process_filter({"order": "propertyName ASC"})
    order = cast(List[OrderNode], ast.order)

    assert len(order) == 1
    assert order[0].field == "propertyName"
    assert order[0].ascending is True

    # Test string format with DESC
    ast = process_filter({"order": "propertyName DESC"})
    order = cast(List[OrderNode], ast.order)

    assert len(order) == 1
    assert order[0].field == "propertyName"
    assert order[0].ascending is False


def test_array_order_format():
    """Test the array format for order: ["propertyName1 ASC", "propertyName2 DESC"]."""
    ast = process_filter({"order": ["propertyName1 ASC", "propertyName2 DESC"]})
    order = cast(List[OrderNode], ast.order)

    assert len(order) == 2
    assert order[0].field == "propertyName1"
    assert order[0].ascending is True
    assert order[1].field == "propertyName2"
    assert order[1].ascending is False


def test_mixed_order_formats():
    """Test mixing both ASC/DESC keywords and minus sign notation."""
    # Using minus sign notation
    ast = process_filter({"order": "-propertyName"})
    order = cast(List[OrderNode], ast.order)

    assert len(order) == 1
    assert order[0].field == "propertyName"
    assert order[0].ascending is False

    # Using array with mixed formats
    ast = process_filter({"order": ["propertyName1 ASC", "-propertyName2"]})
    order = cast(List[OrderNode], ast.order)

    assert len(order) == 2
    assert order[0].field == "propertyName1"
    assert order[0].ascending is True
    assert order[1].field == "propertyName2"
    assert order[1].ascending is False


def test_complex_order_formats():
    """Test more complex order formats, including multiple fields in a string."""
    # Multiple fields in a comma-separated string
    ast = process_filter({"order": "field1 ASC, field2 DESC, -field3"})
    order = cast(List[OrderNode], ast.order)

    assert len(order) == 3
    assert order[0].field == "field1"
    assert order[0].ascending is True
    assert order[1].field == "field2"
    assert order[1].ascending is False
    assert order[2].field == "field3"
    assert order[2].ascending is False


def test_json_string_order():
    """Test order format when provided via JSON string."""
    # Single field in JSON string
    json_filter = '{"order": "propertyName DESC"}'
    parser = FilterParser()
    normalized = FilterNormalizer().normalize(parser.parse(json_filter))
    ast = ASTBuilder().build(normalized)
    order = cast(List[OrderNode], ast.order)

    assert len(order) == 1
    assert order[0].field == "propertyName"
    assert order[0].ascending is False

    # Array format in JSON string
    json_filter = '{"order": ["field1 ASC", "field2 DESC"]}'
    parser = FilterParser()
    normalized = FilterNormalizer().normalize(parser.parse(json_filter))
    ast = ASTBuilder().build(normalized)
    order = cast(List[OrderNode], ast.order)

    assert len(order) == 2
    assert order[0].field == "field1"
    assert order[0].ascending is True
    assert order[1].field == "field2"
    assert order[1].ascending is False


def test_nested_params_order_format():
    """Test order format when provided via nested URL parameters."""
    # Single field in nested params
    nested_params = {"filter[order]": "propertyName DESC"}
    parser = FilterParser()
    normalized = FilterNormalizer().normalize(parser.parse(nested_params))
    ast = ASTBuilder().build(normalized)
    order = cast(List[OrderNode], ast.order)

    assert len(order) == 1
    assert order[0].field == "propertyName"
    assert order[0].ascending is False

    # Multiple fields as array elements in nested params
    nested_params = {
        "filter[order][0]": "field1 ASC",
        "filter[order][1]": "field2 DESC",
    }
    parser = FilterParser()
    normalized = FilterNormalizer().normalize(parser.parse(nested_params))
    ast = ASTBuilder().build(normalized)
    order = cast(List[OrderNode], ast.order)

    # This will work if the parser correctly handles array indices in nested params
    assert len(order) == 2
    assert order[0].field == "field1"
    assert order[0].ascending is True
    assert order[1].field == "field2"
    assert order[1].ascending is False
