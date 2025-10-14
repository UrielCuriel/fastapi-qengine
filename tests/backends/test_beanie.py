"""
Tests for the Beanie backend.
"""

import asyncio as _asyncio
from collections.abc import AsyncGenerator, Mapping
from datetime import date, datetime
from enum import Enum
from typing import cast, get_args, get_origin

import pytest
import pytest_asyncio
from beanie import Document, init_beanie  # pyright: ignore[reportUnknownVariableType]
from beanie.odm.fields import PydanticObjectId
from beanie.odm.queries.aggregation import AggregationQuery
from pydantic import BaseModel
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.mongo_client import AsyncMongoClient
from pymongo.errors import PyMongoError

from fastapi_qengine.backends.beanie import (
    BeanieQueryCompiler,
    BeanieQueryEngine,
)
from fastapi_qengine.core.ast import ASTBuilder
from fastapi_qengine.core.errors import CompilerError, ParseError, ValidationError
from fastapi_qengine.core.normalizer import FilterNormalizer
from fastapi_qengine.core.parser import FilterParser
from fastapi_qengine.core.types import (
    ComparisonOperator,
    FieldCondition,
    FilterAST,
    LogicalCondition,
    OrderNode,
)


# genera un nombre de base de datos de prueba único para cada ejecución de prueba
# para evitar conflictos entre pruebas paralelas
@pytest_asyncio.fixture(scope="function")
async def db_name() -> str:
    import uuid

    return f"test_db_{uuid.uuid4().hex}"


@pytest_asyncio.fixture(scope="function")
async def mongo_client(
    db_name: str,
) -> AsyncGenerator[AsyncMongoClient[Mapping[str, object]], None]:
    uri = "mongodb://localhost:27017"
    # Provide explicit type argument Any to satisfy type checker diagnostics
    mongo_client: AsyncMongoClient[Mapping[str, object]] = AsyncMongoClient(uri)

    # Esperar a que el contenedor esté listo (ping con reintentos)
    for attempt in range(10):
        try:
            admin_db: AsyncDatabase[Mapping[str, object]] = (
                mongo_client.admin
            )  # explicit type
            _ = await admin_db.command(
                {"ping": 1}
            )  # assign result to suppress diagnostic
            break
        except PyMongoError:  # pragma: no cover - solo en caso de arranque lento
            if attempt == 9:
                raise
            await _asyncio.sleep(0.5 * (attempt + 1))

    try:
        yield mongo_client
    finally:
        # Limpieza sin comprobación redundante
        await mongo_client.drop_database(db_name)
        await mongo_client.close()


@pytest_asyncio.fixture()
async def product_model():
    """Fixture for Product model."""

    class Product(Document):
        name: str
        price: float
        category: str
        in_stock: bool
        tags: list[str]

    return Product


@pytest_asyncio.fixture()
async def advanced_model():
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
        stock_count: int | None = None
        tags: list[str] = []

    return AdvancedProduct


@pytest_asyncio.fixture()
async def topmodel_model():
    """Fixture for TopModel model with nested SubModel."""

    class SubModel(BaseModel):
        sub_field: str
        other_field: int

    class TopModel(Document):
        top_field: str
        nested: SubModel
        nested_list: list[SubModel]
        optional_nested: SubModel | None = None
        optional_list: list[SubModel] | None = None

    return TopModel


@pytest_asyncio.fixture(autouse=True, scope="function")
async def db_init(
    db_name: str,
    mongo_client: AsyncMongoClient[Mapping[str, object]],
    product_model: type[Document],
    topmodel_model: type[Document],
    advanced_model: type[Document],
) -> AsyncGenerator[None, None]:
    # Define los modelos a usar en las pruebas
    modelos: list[type[Document]] = [product_model, topmodel_model, advanced_model]

    test_db: AsyncDatabase[Mapping[str, object]] = mongo_client.get_database(db_name)
    await init_beanie(database=test_db, document_models=modelos)
    yield
    for collection_name in await test_db.list_collection_names():
        _ = await test_db[collection_name].delete_many({})


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
    async def test_compile_unsupported_operator(
        self, _beanie_compiler: BeanieQueryCompiler
    ):
        """Test compiling with an unsupported operator raises an error."""
        builder = ASTBuilder()
        # Manually create an AST with an invalid operator
        filter_input = FilterParser().parse({"where": {"price": {"$unsupported": 10}}})
        # This will pass normalization as it allows unknown operators, but fail compilation
        normalized = FilterNormalizer().normalize(filter_input)

        with pytest.raises(ParseError, match="Unknown operator"):
            _ = builder.build(normalized)

    @pytest.mark.asyncio
    async def test_compile_unsupported_logical_operator(
        self, beanie_compiler: BeanieQueryCompiler
    ):
        """Test compiling with an unsupported logical operator raises an error."""
        # Manually create an AST with an invalid logical operator
        ast = FilterAST(
            where=LogicalCondition(
                # pyrefly: ignore
                operator="$unsupported_logical",  # pyright: ignore[reportArgumentType]
                conditions=[
                    FieldCondition(
                        field="price", operator=ComparisonOperator.GT, value=10
                    )
                ],
            )
        )
        with pytest.raises(CompilerError, match="Unsupported logical operator"):
            _ = beanie_compiler.compile(ast)


class TestBeanieQueryEngine:
    """Tests for the high-level BeanieQueryEngine."""

    @pytest_asyncio.fixture
    async def engine(
        self, product_model: type[Document]
    ) -> BeanieQueryEngine[Document]:
        """Fixture for BeanieQueryEngine."""
        return BeanieQueryEngine(model_class=product_model)

    @pytest.mark.asyncio
    async def test_build_query_simple(self, engine: BeanieQueryEngine[Document]):
        """Test building a simple query."""
        filter_input: dict[str, object] = {"where": {"name": "Test"}}
        ast = ASTBuilder().build(
            FilterNormalizer().normalize(FilterParser().parse(filter_input))
        )
        query, projection_model, sort_spec = engine.build_query(ast)

        assert isinstance(query, AggregationQuery)
        # AggregationQuery uses a pipeline instead of find_expressions
        assert len(query.aggregation_pipeline) > 0
        assert {"$match": {"name": "Test"}} in query.aggregation_pipeline
        assert projection_model is None
        assert sort_spec is None

    @pytest.mark.asyncio
    async def test_build_query_complex(self, engine: BeanieQueryEngine[Document]):
        """Test building a complex query with all parts."""
        filter_input: dict[str, object] = {
            "where": {"price": {"$gt": 100}, "category": "electronics"},
            "order": "-price,name",
            "fields": {"name": 1, "price": 1},
        }
        ast = ASTBuilder().build(
            FilterNormalizer().normalize(FilterParser().parse(filter_input))
        )
        query, projection_model, sort_spec = engine.build_query(ast)

        assert isinstance(query, AggregationQuery)
        # Check that the pipeline contains the expected $match stage
        assert {
            "$match": {"$and": [{"price": {"$gt": 100}}, {"category": "electronics"}]}
        } in query.aggregation_pipeline
        # Check that the pipeline contains the expected $sort stage
        assert {"$sort": {"price": -1, "name": 1}} in query.aggregation_pipeline
        # Check that the pipeline contains the expected $project stage
        assert {"$project": {"name": 1, "price": 1}} in query.aggregation_pipeline
        assert sort_spec == [("price", -1), ("name", 1)]
        assert projection_model is not None
        assert "name" in projection_model.model_fields
        assert "price" in projection_model.model_fields
        assert "category" not in projection_model.model_fields

    @pytest.mark.asyncio
    async def test_projection_model_creation_inclusion(
        self, engine: BeanieQueryEngine[Document]
    ):
        """Test inclusion projection model creation."""
        projection_dict = {"name": 1, "price": 1}
        model = engine._create_projection_model(projection_dict)  # pyright: ignore[reportPrivateUsage] #test purpose
        assert model is not None
        assert issubclass(model, BaseModel)
        assert "name" in model.model_fields
        assert "price" in model.model_fields
        assert "category" not in model.model_fields

    @pytest.mark.asyncio
    async def test_projection_model_creation_exclusion(
        self, engine: BeanieQueryEngine[Document]
    ):
        """Test exclusion projection model creation."""
        projection_dict = {"category": 0, "in_stock": 0}
        model = engine._create_projection_model(projection_dict)  # pyright: ignore[reportPrivateUsage] #test purpose
        assert model is not None
        assert "name" in model.model_fields
        assert "price" in model.model_fields
        assert "category" not in model.model_fields
        assert "in_stock" not in model.model_fields

    @pytest.mark.asyncio
    async def test_projection_with_nested_models(self, topmodel_model: type[Document]):
        """Test projection with nested Pydantic models."""
        engine = BeanieQueryEngine(model_class=topmodel_model)

        # Helper type guards to reduce Any usage from typing.get_args and satisfy diagnostics
        from typing import TypeGuard

        def _is_basemodel_type(t: object) -> TypeGuard[type[BaseModel]]:
            return isinstance(t, type) and issubclass(t, BaseModel)

        # Test simple nested inclusion
        proj_model = engine._create_projection_model({"nested.sub_field": 1})  # pyright: ignore[reportPrivateUsage]
        assert proj_model is not None
        assert "nested" in proj_model.model_fields

        nested_annotation = proj_model.model_fields["nested"].annotation

        # Resolve the projected nested model type (handle Optional/Union)
        nested_proj_type: type[BaseModel] | None = None
        if _is_basemodel_type(nested_annotation):
            nested_proj_type = nested_annotation
        else:
            for candidate in cast(tuple[object, object], get_args(nested_annotation)):
                if _is_basemodel_type(candidate):
                    nested_proj_type = candidate
                    break

        assert nested_proj_type is not None, "No projected nested model type found"
        assert "sub_field" in nested_proj_type.model_fields
        assert "other_field" not in nested_proj_type.model_fields

        # Test list of nested models
        proj_model_list = engine._create_projection_model({"nested_list.sub_field": 1})  # pyright: ignore[reportPrivateUsage]
        assert proj_model_list is not None
        assert "nested_list" in proj_model_list.model_fields

        list_annotation = proj_model_list.model_fields["nested_list"].annotation

        item_type: type[BaseModel] | None = None
        origin = get_origin(list_annotation)
        if origin is list:
            inner_args = get_args(list_annotation)
            if inner_args:
                inner_candidate = cast(object, inner_args[0])
                if _is_basemodel_type(inner_candidate):
                    item_type = inner_candidate
        else:
            # Possibly Optional[...] wrapping List[...] -> scan union args
            for union_arg in cast(tuple[object, object], get_args(list_annotation)):
                if get_origin(union_arg) is list:
                    inner_list_args = cast(tuple[object, object], get_args(union_arg))
                    if inner_list_args:
                        inner_candidate = inner_list_args[0]
                        if _is_basemodel_type(inner_candidate):
                            item_type = inner_candidate
                            break

        assert item_type is not None, "Could not determine list item annotation"
        assert "sub_field" in item_type.model_fields
        assert "other_field" not in item_type.model_fields

    @pytest.mark.asyncio
    async def test_projection_creation_failure(
        self, engine: BeanieQueryEngine[Document]
    ):
        """Test that projection creation failure returns None."""
        # Invalid field name
        model = engine._create_projection_model({"non_existent_field": 1})  # pyright: ignore[reportPrivateUsage]
        assert model is None

    @pytest.mark.asyncio
    async def test_execute_query(self, engine: BeanieQueryEngine[Document]):
        """Test the execute_query method."""
        filter_input: dict[str, object] = {"where": {"name": "Test"}}
        ast = ASTBuilder().build(
            FilterNormalizer().normalize(FilterParser().parse(filter_input))
        )
        query, projection_model, sort_spec = engine.execute_query(ast)
        assert isinstance(query, AggregationQuery)
        # AggregationQuery uses a pipeline instead of find_expressions
        assert len(query.aggregation_pipeline) > 0
        assert {"$match": {"name": "Test"}} in query.aggregation_pipeline
        assert projection_model is None
        assert sort_spec is None


class TestBeanieFieldValidation:
    """Tests for field validation in the BeanieQueryEngine."""

    @pytest_asyncio.fixture
    async def engine(
        self, advanced_model: type[Document]
    ) -> BeanieQueryEngine[Document]:
        """Fixture for BeanieQueryEngine with advanced model."""
        return BeanieQueryEngine(model_class=advanced_model)

    @pytest.mark.asyncio
    async def test_field_validation_invalid_field(
        self, engine: BeanieQueryEngine[Document]
    ):
        """Test validation of non-existent fields raises ValidationError."""
        with pytest.raises(ValidationError, match="does not exist"):
            engine._validate_field_exists("non_existent_field")  # pyright: ignore[reportPrivateUsage]

    @pytest.mark.asyncio
    async def test_field_validation_special_fields(
        self, engine: BeanieQueryEngine[Document]
    ):
        """Test validation passes for special fields like _id."""
        # These should not raise exceptions
        engine._validate_field_exists("_id")  # pyright: ignore[reportPrivateUsage]
        engine._validate_field_exists("id")  # pyright: ignore[reportPrivateUsage]
        engine._validate_field_exists("$and")  # pyright: ignore[reportPrivateUsage]

    @pytest.mark.asyncio
    async def test_transform_objectid(self, engine: BeanieQueryEngine[Document]):
        """Test transformation of string to ObjectId."""
        object_id_str = "507f1f77bcf86cd799439011"
        # pyrefly: ignore
        transformed = engine._transform_value("product_id", "$eq", object_id_str)  # pyright: ignore[reportPrivateUsage, reportArgumentType]
        assert isinstance(transformed, PydanticObjectId)
        assert str(transformed) == object_id_str

    @pytest.mark.asyncio
    async def test_transform_datetime(self, engine: BeanieQueryEngine[Document]):
        """Test transformation of ISO string to datetime."""
        date_str = "2023-01-15T10:30:45"
        # pyrefly: ignore
        transformed = engine._transform_value("created_at", "$eq", date_str)  # pyright: ignore[reportPrivateUsage, reportArgumentType]
        assert isinstance(transformed, datetime)
        assert transformed.year == 2023
        assert transformed.month == 1
        assert transformed.day == 15
        assert transformed.hour == 10
        assert transformed.minute == 30

    @pytest.mark.asyncio
    async def test_transform_date(self, engine: BeanieQueryEngine[Document]):
        """Test transformation of ISO string to date."""
        date_str = "2023-01-15"
        # pyrefly: ignore
        transformed = engine._transform_value("release_date", "$eq", date_str)  # pyright: ignore[reportPrivateUsage, reportArgumentType]
        assert isinstance(transformed, date)
        assert transformed.year == 2023
        assert transformed.month == 1
        assert transformed.day == 15

    @pytest.mark.asyncio
    async def test_transform_enum(self, engine: BeanieQueryEngine[Document]):
        """Test transformation of string to enum."""
        transformed = engine._transform_value(  # pyright: ignore[reportPrivateUsage]
            "status", ComparisonOperator.EQ, "available"
        )
        transformed_enum = cast(Enum, transformed)
        assert transformed_enum.value == "available"  # pyright: ignore[reportAny]

        # Test with invalid enum value
        invalid_value = "invalid_status"
        transformed_invalid = engine._transform_value(  # pyright: ignore[reportPrivateUsage]
            "status", ComparisonOperator.EQ, invalid_value
        )
        # Should return original value if transformation fails
        assert transformed_invalid == invalid_value

    @pytest.mark.asyncio
    async def test_transform_list_values(self, engine: BeanieQueryEngine[Document]):
        """Test transformation of list values for $in operator."""
        object_id_list = ["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439022"]
        # pyrefly: ignore
        transformed = engine._transform_value("product_id", "$in", object_id_list)  # pyright: ignore[reportPrivateUsage, reportArgumentType]
        assert isinstance(transformed, list)
        items = cast(list[object], transformed)
        assert all(isinstance(obj, PydanticObjectId) for obj in items)

    @pytest.mark.asyncio
    async def test_transform_scalar_types(self, engine: BeanieQueryEngine[Document]):
        """Test basic scalar type transformations."""
        # Integer
        # pyrefly: ignore
        transformed_int = engine._transform_value("stock_count", "$eq", "42")  # pyright: ignore[reportPrivateUsage, reportArgumentType]
        assert isinstance(transformed_int, int)
        assert transformed_int == 42

        # Boolean
        # pyrefly: ignore
        transformed_bool = engine._transform_value("in_stock", "$eq", "true")  # pyright: ignore[reportPrivateUsage, reportArgumentType]
        assert isinstance(transformed_bool, bool)
        assert transformed_bool is True

        # Float
        # pyrefly: ignore
        transformed_float = engine._transform_value("price", "$eq", "19.99")  # pyright: ignore[reportArgumentType, reportPrivateUsage]
        assert isinstance(transformed_float, float)
        assert transformed_float == 19.99

    @pytest.mark.asyncio
    async def test_validation_in_ast_processing(
        self, engine: BeanieQueryEngine[Document]
    ):
        """Test that validation happens during AST processing."""
        # Create an AST with invalid field
        ast = FilterAST(
            where=FieldCondition(
                field="non_existent", operator=ComparisonOperator.EQ, value="test"
            ),
            order=[OrderNode(field="price", ascending=True)],
        )

        # Should raise ValidationError during processing
        with pytest.raises(ValidationError, match="does not exist"):
            _ = engine._validate_and_transform_ast(ast)  # pyright: ignore[reportPrivateUsage]

    @pytest.mark.asyncio
    async def test_skip_invalid_fields_in_order(
        self, engine: BeanieQueryEngine[Document]
    ):
        """Test that invalid fields in order are skipped."""
        # Create an AST with both valid and invalid order fields
        ast = FilterAST(
            order=[
                OrderNode(field="price", ascending=True),
                OrderNode(field="non_existent", ascending=False),
            ]
        )

        # Should skip the invalid field but keep the valid one
        result_ast = engine._validate_and_transform_ast(ast)  # pyright: ignore[reportPrivateUsage]
        assert result_ast.order is not None
        orders = result_ast.order
        assert len(orders) == 1
        assert orders[0].field == "price"

    @pytest.mark.asyncio
    async def test_validate_field_projection(self, engine: BeanieQueryEngine[Document]):
        """Test validation of fields in projection."""
        from fastapi_qengine.core.types import FieldsNode

        # Create fields projection with valid and invalid fields
        fields_node = FieldsNode(
            fields={"name": 1, "price": 1, "non_existent_field": 1}
        )

        ast = FilterAST(fields=fields_node)
        result_ast = engine._validate_and_transform_ast(ast)  # pyright: ignore[reportPrivateUsage]
        # Should be defined fields in resutl ast
        assert result_ast.fields is not None
        # Should include only valid fields in the projection
        assert "name" in result_ast.fields.fields
        assert "price" in result_ast.fields.fields
        assert "non_existent_field" not in result_ast.fields.fields
        assert len(result_ast.fields.fields) == 2
