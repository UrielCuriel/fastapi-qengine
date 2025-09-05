"""
Tests for the Beanie backend.
"""

from datetime import date, datetime
from enum import Enum
from typing import AsyncGenerator, List, Optional, get_args

import pytest
import pytest_asyncio
from beanie import Document, init_beanie
from beanie.odm.fields import PydanticObjectId
from beanie.odm.queries.find import FindMany
from pydantic import BaseModel
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.mongo_client import AsyncMongoClient

from fastapi_qengine.backends.beanie import (
    BeanieQueryCompiler,
    BeanieQueryEngine,
    compile_to_mongodb,
)
from fastapi_qengine.core.ast import ASTBuilder, FieldCondition, LogicalCondition
from fastapi_qengine.core.errors import CompilerError, ParseError, ValidationError
from fastapi_qengine.core.normalizer import FilterNormalizer
from fastapi_qengine.core.parser import FilterParser
from fastapi_qengine.core.types import (
    ComparisonOperator,
    FilterAST,
    OrderNode,
)


# genera un nombre de base de datos de prueba único para cada ejecución de prueba
# para evitar conflictos entre pruebas paralelas
@pytest_asyncio.fixture(scope="function")
async def db_name() -> str:
    import uuid

    return f"test_db_{uuid.uuid4().hex}"


@pytest_asyncio.fixture(scope="function")
async def mongo_client(db_name: str) -> AsyncGenerator[AsyncMongoClient, None]:
    uri = "mongodb://localhost:27017"
    mongo_client = AsyncMongoClient(uri)
    # Esperar a que el contenedor esté listo (ping con reintentos)
    import asyncio as _asyncio

    from pymongo.errors import PyMongoError

    for attempt in range(10):
        try:
            await mongo_client.admin.command({"ping": 1})
            break
        except PyMongoError:  # pragma: no cover - solo en caso de arranque lento
            if attempt == 9:
                raise
            await _asyncio.sleep(0.5 * (attempt + 1))
    yield mongo_client
    if mongo_client is not None:
        await mongo_client.drop_database(db_name)
        await mongo_client.close()
        mongo_client = None


@pytest_asyncio.fixture
def product_model():
    """Fixture for Product model."""

    class Product(Document):
        name: str
        price: float
        category: str
        in_stock: bool
        tags: List[str]

    return Product


@pytest_asyncio.fixture
def advanced_model():
    """Fixture for a model with advanced types for testing transformations."""

    class ProductStatus(Enum):
        AVAILABLE = "available"
        SOLD_OUT = "sold_out"
        DISCONTINUED = "discontinued"

    class AdvancedProduct(Document):
        product_id: PydanticObjectId
        name: str
        price: float
        status: ProductStatus
        created_at: datetime
        release_date: date
        in_stock: bool
        stock_count: Optional[int] = None
        tags: List[str] = []

    return AdvancedProduct


@pytest_asyncio.fixture
def topmodel_model():
    """Fixture for TopModel model with nested SubModel."""

    class SubModel(BaseModel):
        sub_field: str
        other_field: int

    class TopModel(Document):
        top_field: str
        nested: SubModel
        nested_list: List[SubModel]
        optional_nested: Optional[SubModel] = None
        optional_list: Optional[List[SubModel]] = None

    return TopModel


@pytest_asyncio.fixture(autouse=True, scope="function")
async def db_init(
    db_name: str, mongo_client: AsyncMongoClient, product_model, topmodel_model, advanced_model
) -> AsyncGenerator[None, None]:
    # Define los modelos a usar en las pruebas
    modelos: list[type[Document]] = [product_model, topmodel_model, advanced_model]

    test_db: AsyncDatabase = mongo_client.get_database(db_name)
    await init_beanie(database=test_db, document_models=modelos)
    yield
    for collection_name in await test_db.list_collection_names():
        await test_db[collection_name].delete_many({})


@pytest.fixture
def beanie_compiler() -> BeanieQueryCompiler:
    """Fixture for BeanieQueryCompiler."""
    return BeanieQueryCompiler()


class TestBeanieCompiler:
    """Test Beanie query compilation."""

    @pytest.mark.asyncio
    async def test_compile_simple_condition(self, beanie_compiler: BeanieQueryCompiler):
        """Test compiling simple condition to MongoDB format."""
        builder = ASTBuilder()
        normalizer = FilterNormalizer()

        filter_input = FilterParser().parse({"where": {"category": "electronics"}})
        normalized = normalizer.normalize(filter_input)
        ast = builder.build(normalized)
        query = beanie_compiler.compile(ast)
        assert query["filter"] == {"category": "electronics"}

    @pytest.mark.asyncio
    async def test_compile_unsupported_operator(self, beanie_compiler: BeanieQueryCompiler):
        """Test compiling with an unsupported operator raises an error."""
        builder = ASTBuilder()
        # Manually create an AST with an invalid operator
        filter_input = FilterParser().parse({"where": {"price": {"$unsupported": 10}}})
        # This will pass normalization as it allows unknown operators, but fail compilation
        normalized = FilterNormalizer().normalize(filter_input)

        with pytest.raises(ParseError, match="Unknown operator"):
            builder.build(normalized)

    @pytest.mark.asyncio
    async def test_compile_unsupported_logical_operator(self, beanie_compiler: BeanieQueryCompiler):
        """Test compiling with an unsupported logical operator raises an error."""
        # Manually create an AST with an invalid logical operator
        ast = FilterAST(
            where=LogicalCondition(
                operator="$unsupported_logical",  # type: ignore
                conditions=[FieldCondition(field="price", operator=ComparisonOperator.GT, value=10)],
            )
        )
        with pytest.raises(CompilerError, match="Unsupported logical operator"):
            beanie_compiler.compile(ast)


class TestBeanieQueryEngine:
    """Tests for the high-level BeanieQueryEngine."""

    @pytest_asyncio.fixture
    async def engine(self, product_model) -> BeanieQueryEngine:
        """Fixture for BeanieQueryEngine."""
        return BeanieQueryEngine(model_class=product_model)

    @pytest.mark.asyncio
    async def test_build_query_simple(self, engine, product_model):
        """Test building a simple query."""
        filter_input = {"where": {"name": "Test"}}
        ast = ASTBuilder().build(FilterNormalizer().normalize(FilterParser().parse(filter_input)))
        query, projection_model, sort_spec = engine.build_query(ast)

        assert isinstance(query, FindMany)
        assert query.find_expressions == [{"name": "Test"}]
        assert projection_model is None
        assert sort_spec is None

    @pytest.mark.asyncio
    async def test_build_query_complex(self, engine, product_model):
        """Test building a complex query with all parts."""
        filter_input = {
            "where": {"price": {"$gt": 100}, "category": "electronics"},
            "order": "-price,name",
            "fields": {"name": 1, "price": 1},
        }
        ast = ASTBuilder().build(FilterNormalizer().normalize(FilterParser().parse(filter_input)))
        query, projection_model, sort_spec = engine.build_query(ast)

        assert query.find_expressions == [{"$and": [{"price": {"$gt": 100}}, {"category": "electronics"}]}]
        assert sort_spec == [("price", -1), ("name", 1)]
        assert projection_model is not None
        assert "name" in projection_model.model_fields
        assert "price" in projection_model.model_fields
        assert "category" not in projection_model.model_fields

    @pytest.mark.asyncio
    async def test_projection_model_creation_inclusion(self, engine, product_model):
        """Test inclusion projection model creation."""
        projection_dict = {"name": 1, "price": 1}
        model = engine._create_projection_model(projection_dict)
        assert model is not None
        assert issubclass(model, BaseModel)
        assert "name" in model.model_fields
        assert "price" in model.model_fields
        assert "category" not in model.model_fields

    @pytest.mark.asyncio
    async def test_projection_model_creation_exclusion(self, engine, product_model):
        """Test exclusion projection model creation."""
        projection_dict = {"category": 0, "in_stock": 0}
        model = engine._create_projection_model(projection_dict)
        assert model is not None
        assert "name" in model.model_fields
        assert "price" in model.model_fields
        assert "category" not in model.model_fields
        assert "in_stock" not in model.model_fields

    @pytest.mark.asyncio
    async def test_projection_with_nested_models(self, topmodel_model):
        """Test projection with nested Pydantic models."""
        engine = BeanieQueryEngine(model_class=topmodel_model)

        # Test simple nested inclusion
        proj_model = engine._create_projection_model({"nested.sub_field": 1})
        assert proj_model is not None
        assert "nested" in proj_model.model_fields
        nested_proj_type = get_args(proj_model.model_fields["nested"].annotation)[0]  # Extract from Optional[Type]
        assert "sub_field" in nested_proj_type.model_fields
        assert "other_field" not in nested_proj_type.model_fields

        # Test list of nested models
        proj_model_list = engine._create_projection_model({"nested_list.sub_field": 1})
        assert proj_model_list is not None
        list_type = proj_model_list.model_fields["nested_list"].annotation
        list_item_type = get_args(get_args(list_type)[0])[0]  # Optional[List[SubProj]] -> SubProj
        assert "sub_field" in list_item_type.model_fields
        assert "other_field" not in list_item_type.model_fields

    @pytest.mark.asyncio
    async def test_projection_creation_failure(self, engine, product_model):
        """Test that projection creation failure returns None."""
        # Invalid field name
        model = engine._create_projection_model({"non_existent_field": 1})
        assert model is None

    @pytest.mark.asyncio
    async def test_execute_query(self, engine, product_model):
        """Test the execute_query method."""
        filter_input = {"where": {"name": "Test"}}
        ast = ASTBuilder().build(FilterNormalizer().normalize(FilterParser().parse(filter_input)))
        query, projection_model, sort_spec = engine.execute_query(ast)
        assert isinstance(query, FindMany)
        assert query.find_expressions == [{"name": "Test"}]
        assert projection_model is None
        assert sort_spec is None


@pytest.mark.asyncio
async def test_compile_to_mongodb_convenience_function():
    """Test the compile_to_mongodb convenience function."""
    filter_input = {
        "where": {"price": {"$gt": 10}},
        "order": "-price",
        "fields": {"name": 1},
    }
    ast = ASTBuilder().build(FilterNormalizer().normalize(FilterParser().parse(filter_input)))
    mongo_query = compile_to_mongodb(ast)

    assert mongo_query["filter"] == {"price": {"$gt": 10}}
    assert mongo_query["sort"] == [("price", -1)]
    assert mongo_query["projection"] == {"name": 1}


class TestBeanieFieldValidation:
    """Tests for field validation in the BeanieQueryEngine."""

    @pytest_asyncio.fixture
    async def engine(self, advanced_model) -> BeanieQueryEngine:
        """Fixture for BeanieQueryEngine with advanced model."""
        return BeanieQueryEngine(model_class=advanced_model)

    @pytest.mark.asyncio
    async def test_field_validation_invalid_field(self, engine):
        """Test validation of non-existent fields raises ValidationError."""
        with pytest.raises(ValidationError, match="does not exist"):
            engine._validate_field_exists("non_existent_field")

    @pytest.mark.asyncio
    async def test_field_validation_special_fields(self, engine):
        """Test validation passes for special fields like _id."""
        # These should not raise exceptions
        engine._validate_field_exists("_id")
        engine._validate_field_exists("id")
        engine._validate_field_exists("$and")  # MongoDB operator

    @pytest.mark.asyncio
    async def test_transform_objectid(self, engine):
        """Test transformation of string to ObjectId."""
        object_id_str = "507f1f77bcf86cd799439011"
        transformed = engine._transform_value("product_id", "$eq", object_id_str)
        assert isinstance(transformed, PydanticObjectId)
        assert str(transformed) == object_id_str

    @pytest.mark.asyncio
    async def test_transform_datetime(self, engine):
        """Test transformation of ISO string to datetime."""
        date_str = "2023-01-15T10:30:45"
        transformed = engine._transform_value("created_at", "$eq", date_str)
        assert isinstance(transformed, datetime)
        assert transformed.year == 2023
        assert transformed.month == 1
        assert transformed.day == 15
        assert transformed.hour == 10
        assert transformed.minute == 30

    @pytest.mark.asyncio
    async def test_transform_date(self, engine):
        """Test transformation of ISO string to date."""
        date_str = "2023-01-15"
        transformed = engine._transform_value("release_date", "$eq", date_str)
        assert isinstance(transformed, date)
        assert transformed.year == 2023
        assert transformed.month == 1
        assert transformed.day == 15

    @pytest.mark.asyncio
    async def test_transform_enum(self, engine):
        """Test transformation of string to enum."""
        transformed = engine._transform_value("status", "$eq", "available")
        assert transformed.value == "available"

        # Test with invalid enum value
        invalid_value = "invalid_status"
        transformed_invalid = engine._transform_value("status", "$eq", invalid_value)
        # Should return original value if transformation fails
        assert transformed_invalid == invalid_value

    @pytest.mark.asyncio
    async def test_transform_list_values(self, engine):
        """Test transformation of list values for $in operator."""
        object_id_list = ["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439022"]
        transformed = engine._transform_value("product_id", "$in", object_id_list)
        assert isinstance(transformed, list)
        assert all(isinstance(item, PydanticObjectId) for item in transformed)

    @pytest.mark.asyncio
    async def test_transform_scalar_types(self, engine):
        """Test basic scalar type transformations."""
        # Integer
        transformed_int = engine._transform_value("stock_count", "$eq", "42")
        assert isinstance(transformed_int, int)
        assert transformed_int == 42

        # Boolean
        transformed_bool = engine._transform_value("in_stock", "$eq", "true")
        assert isinstance(transformed_bool, bool)
        assert transformed_bool is True

        # Float
        transformed_float = engine._transform_value("price", "$eq", "19.99")
        assert isinstance(transformed_float, float)
        assert transformed_float == 19.99

    @pytest.mark.asyncio
    async def test_validation_in_ast_processing(self, engine):
        """Test that validation happens during AST processing."""
        # Create an AST with invalid field
        ast = FilterAST(
            where=FieldCondition(field="non_existent", operator=ComparisonOperator.EQ, value="test"),
            order=[OrderNode(field="price", ascending=True)],
        )

        # Should raise ValidationError during processing
        with pytest.raises(ValidationError, match="does not exist"):
            engine._validate_and_transform_ast(ast)

    @pytest.mark.asyncio
    async def test_skip_invalid_fields_in_order(self, engine, advanced_model):
        """Test that invalid fields in order are skipped."""
        # Create an AST with both valid and invalid order fields
        ast = FilterAST(
            order=[OrderNode(field="price", ascending=True), OrderNode(field="non_existent", ascending=False)]
        )

        # Should skip the invalid field but keep the valid one
        result_ast = engine._validate_and_transform_ast(ast)
        assert len(result_ast.order) == 1
        assert result_ast.order[0].field == "price"

    @pytest.mark.asyncio
    async def test_validate_field_projection(self, engine):
        """Test validation of fields in projection."""
        from fastapi_qengine.core.types import FieldsNode

        # Create fields projection with valid and invalid fields
        fields_node = FieldsNode(fields={"name": 1, "price": 1, "non_existent_field": 1})

        ast = FilterAST(fields=fields_node)
        result_ast = engine._validate_and_transform_ast(ast)

        # Should include only valid fields in the projection
        assert "name" in result_ast.fields.fields
        assert "price" in result_ast.fields.fields
        assert "non_existent_field" not in result_ast.fields.fields
        assert len(result_ast.fields.fields) == 2
