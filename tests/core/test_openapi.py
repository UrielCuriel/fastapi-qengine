"""
Tests for OpenAPI schema generation.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

from fastapi_qengine.openapi_schema import FilterSchemaGenerator, generate_filter_docs


class SimpleModel(BaseModel):
    """A simple model for testing."""

    name: str
    age: int
    is_active: bool


class ComplexModel(BaseModel):
    """A complex model with various types."""

    id: int = Field(description="The unique identifier")
    description: Optional[str] = None
    created_at: datetime
    due_date: date
    price: Decimal
    tags: List[str]


class TestFilterSchemaGenerator:
    """Tests for the FilterSchemaGenerator class."""

    def test_pydantic_v2_extraction(self):
        """Test field extraction from a Pydantic v2 model."""
        generator = FilterSchemaGenerator(model_class=ComplexModel)
        fields = generator._get_model_fields()
        assert "id" in fields
        assert fields["id"]["type"] == int
        assert fields["id"]["description"] == "The unique identifier"
        assert "description" in fields
        assert fields["description"]["type"] == Optional[str]

    def test_type_mapping(self):
        """Test the conversion from Python types to OpenAPI types."""
        generator = FilterSchemaGenerator(model_class=SimpleModel)
        assert generator._get_openapi_type(str) == {"type": "string"}
        assert generator._get_openapi_type(int) == {"type": "integer"}
        assert generator._get_openapi_type(bool) == {"type": "boolean"}
        assert generator._get_openapi_type(datetime) == {
            "type": "string",
            "format": "date-time",
        }
        assert generator._get_openapi_type(date) == {"type": "string", "format": "date"}
        assert generator._get_openapi_type(Decimal) == {"type": "number"}
        assert generator._get_openapi_type(List[str]) == {
            "type": "array",
            "items": {"type": "string"},
        }
        assert generator._get_openapi_type(Optional[int]) == {"type": "integer"}

    def test_generate_field_schema(self):
        """Test the generation of a schema for a single field."""
        generator = FilterSchemaGenerator(model_class=SimpleModel)
        field_info = {"type": str}
        schema = generator.generate_field_schema("name", field_info)
        assert "anyOf" in schema
        assert len(schema["anyOf"]) == 2
        assert schema["anyOf"][0]["type"] == "string"
        assert schema["anyOf"][1]["type"] == "object"

    def test_generate_filter_schema(self):
        """Test the generation of the complete filter schema."""
        generator = FilterSchemaGenerator(model_class=SimpleModel)
        schema = generator.generate_filter_schema()
        assert schema["type"] == "object"
        assert "where" in schema["properties"]
        assert "order" in schema["properties"]
        assert "fields" in schema["properties"]
        assert "name" in schema["properties"]["where"]["properties"]
        assert "$and" in schema["properties"]["where"]["properties"]

    def test_generate_examples(self):
        """Test the generation of examples."""
        generator = FilterSchemaGenerator(model_class=SimpleModel)
        examples = generator.generate_examples()
        assert "simple" in examples
        assert "operators" in examples
        assert "logical" in examples
        assert "complete" in examples
        assert '{"where":{"name":"example"}}' in examples["simple"]["value"]

    def test_fallback_field_extraction(self):
        """Test field extraction when the model is not a Pydantic model."""

        class NotAModel:
            name: str
            value: int

        generator = FilterSchemaGenerator(model_class=NotAModel)
        fields = generator._get_model_fields()
        assert "name" in fields
        assert fields["name"]["type"] == str
        assert "value" in fields
        assert fields["value"]["type"] == int

    def test_basic_fallback(self):
        """Test the most basic fallback for field extraction."""

        class EmptyClass:
            pass

        # This should trigger the basic fallback
        generator = FilterSchemaGenerator(model_class=EmptyClass)
        fields = generator._get_basic_fallback_fields()
        assert "id" in fields
        assert "name" in fields


def test_generate_filter_docs_function():
    """Test the main generate_filter_docs function."""
    docs = generate_filter_docs(model_class=SimpleModel)
    assert "schemas" in docs
    assert "SimpleModelFilter" in docs["schemas"]
    assert "parameters" in docs
    assert "SimpleModelFilterParam" in docs["parameters"]
    assert "examples" in docs
    assert "simple" in docs["examples"]
