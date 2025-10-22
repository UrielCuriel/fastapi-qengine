"""
Integration test for Beanie backend with validation and transformation.
"""

from collections.abc import AsyncGenerator, Mapping
from datetime import date, datetime
from enum import Enum

import pytest
import pytest_asyncio
from beanie import Document, init_beanie  # pyright: ignore[reportUnknownVariableType]
from beanie.odm.fields import PydanticObjectId
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.mongo_client import AsyncMongoClient

from fastapi_qengine.backends.beanie import BeanieQueryEngine
from fastapi_qengine.core.ast import ASTBuilder
from fastapi_qengine.core.normalizer import FilterNormalizer
from fastapi_qengine.core.parser import FilterParser
from fastapi_qengine.core.types import FilterAST


class ProductStatus(Enum):
    """Product status enumeration."""

    AVAILABLE = "available"
    SOLD_OUT = "sold_out"
    DISCONTINUED = "discontinued"


class AdvancedProduct(Document):
    """Advanced product model with various field types."""

    product_id: PydanticObjectId
    name: str
    price: float
    status: ProductStatus
    created_at: datetime
    release_date: date
    in_stock: bool
    stock_count: int | None = None
    tags: list[str] = []


# genera un nombre de base de datos de prueba único para cada ejecución de prueba
# para evitar conflictos entre pruebas paralelas
@pytest_asyncio.fixture(scope="function")
async def db_name() -> str:
    import uuid

    return f"test_integration_db_{uuid.uuid4().hex}"


@pytest_asyncio.fixture(scope="function")
async def mongo_client(
    db_name: str,
) -> AsyncGenerator[AsyncMongoClient[Mapping[str, object]], None]:
    """MongoDB client fixture."""
    uri = "mongodb://localhost:27017"
    mongo_client = AsyncMongoClient[Mapping[str, object]](uri)
    # Wait for container to be ready
    import asyncio as _asyncio

    from pymongo.errors import PyMongoError

    for attempt in range(10):
        try:
            _ = await mongo_client.admin.command({"ping": 1})
            break
        except PyMongoError:
            if attempt == 9:
                raise
            await _asyncio.sleep(0.5 * (attempt + 1))
    yield mongo_client
    # delete test database
    await mongo_client.drop_database(db_name)
    await mongo_client.close()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def db_init(mongo_client: AsyncMongoClient[Mapping[str, object]], db_name: str) -> AsyncGenerator[None, None]:
    """Initialize database with sample data."""
    test_db: AsyncDatabase[Mapping[str, object]] = mongo_client.get_database(db_name)
    await init_beanie(database=test_db, document_models=[AdvancedProduct])

    # Create sample products
    sample_products = [
        AdvancedProduct(
            product_id=PydanticObjectId(),
            name="Laptop Pro",
            price=1299.99,
            status=ProductStatus.AVAILABLE,
            created_at=datetime.fromisoformat("2023-01-15T10:00:00"),
            release_date=date.fromisoformat("2022-12-01"),
            in_stock=True,
            stock_count=50,
            tags=["electronics", "computer"],
        ),
        AdvancedProduct(
            product_id=PydanticObjectId(),
            name="Basic Mouse",
            price=19.99,
            status=ProductStatus.SOLD_OUT,
            created_at=datetime.fromisoformat("2023-02-20T14:30:00"),
            release_date=date.fromisoformat("2022-01-15"),
            in_stock=False,
            stock_count=0,
            tags=["electronics", "accessory"],
        ),
        AdvancedProduct(
            product_id=PydanticObjectId(),
            name="Gaming Keyboard",
            price=89.99,
            status=ProductStatus.AVAILABLE,
            created_at=datetime.fromisoformat("2023-03-10T09:15:00"),
            release_date=date.fromisoformat("2022-06-30"),
            in_stock=True,
            stock_count=25,
            tags=["electronics", "gaming"],
        ),
        AdvancedProduct(
            product_id=PydanticObjectId(),
            name="Vintage Monitor",
            price=149.99,
            status=ProductStatus.DISCONTINUED,
            created_at=datetime.fromisoformat("2020-05-05T11:45:00"),
            release_date=date.fromisoformat("2018-03-10"),
            in_stock=True,
            stock_count=5,
            tags=["electronics", "vintage"],
        ),
    ]

    _ = await AdvancedProduct.insert_many(sample_products)
    yield
    for collection_name in await test_db.list_collection_names():
        _ = await test_db[collection_name].delete_many({})


@pytest_asyncio.fixture
async def engine() -> BeanieQueryEngine[Document]:
    """BeanieQueryEngine instance."""
    return BeanieQueryEngine[Document](model_class=AdvancedProduct)


@pytest.mark.asyncio
async def test_query_with_date_transformation(
    engine: BeanieQueryEngine[AdvancedProduct],
) -> None:
    """Test querying with date transformations."""
    # Query products released after a specific date
    filter_input: dict[str, object] = {"where": {"release_date": {"$gte": "2022-06-01"}}}

    ast: FilterAST = ASTBuilder().build(FilterNormalizer().normalize(FilterParser().parse(filter_input)))
    query, _, _ = engine.build_query(ast)
    results: list[AdvancedProduct] = await query.to_list()

    # Should return products released on or after June 1, 2022
    assert len(results) == 2
    product_names: list[str] = [p.name for p in results]
    assert "Laptop Pro" in product_names
    assert "Gaming Keyboard" in product_names


@pytest.mark.asyncio
async def test_query_with_enum_transformation(
    engine: BeanieQueryEngine[AdvancedProduct],
) -> None:
    """Test querying with enum transformations."""
    # Query products with AVAILABLE status
    filter_input: dict[str, object] = {"where": {"status": "available"}}

    ast: FilterAST = ASTBuilder().build(FilterNormalizer().normalize(FilterParser().parse(filter_input)))
    query, _, _ = engine.build_query(ast)
    results: list[AdvancedProduct] = await query.to_list()

    # Should return only available products
    assert len(results) == 2
    for product in results:
        assert product.status == ProductStatus.AVAILABLE


@pytest.mark.asyncio
async def test_query_with_list_transformation(
    engine: BeanieQueryEngine[AdvancedProduct],
) -> None:
    """Test querying with list transformations."""
    # Query products with specific tags
    filter_input: dict[str, object] = {"where": {"tags": {"$in": ["gaming", "vintage"]}}}

    ast: FilterAST = ASTBuilder().build(FilterNormalizer().normalize(FilterParser().parse(filter_input)))
    query, _, _ = engine.build_query(ast)
    results: list[AdvancedProduct] = await query.to_list()

    # Should return gaming and vintage products
    assert len(results) == 2
    product_names: list[str] = [p.name for p in results]
    assert "Gaming Keyboard" in product_names
    assert "Vintage Monitor" in product_names


@pytest.mark.asyncio
async def test_query_with_multiple_transformations(
    engine: BeanieQueryEngine[AdvancedProduct],
) -> None:
    """Test querying with multiple field transformations."""
    # Complex query with multiple fields and transformations
    filter_input: dict[str, object] = {
        "where": {
            "price": {"$lt": 100},
            "status": "available",
            "created_at": {"$gte": "2023-03-01T00:00:00"},
        }
    }

    ast: FilterAST = ASTBuilder().build(FilterNormalizer().normalize(FilterParser().parse(filter_input)))
    query, _, _ = engine.build_query(ast)
    results: list[AdvancedProduct] = await query.to_list()

    # Should return available products under $100 created in March 2023 or later
    assert len(results) == 1
    assert results[0].name == "Gaming Keyboard"


@pytest.mark.asyncio
async def test_query_with_invalid_field_skipping(
    engine: BeanieQueryEngine[Document],
) -> None:
    """Test that invalid fields in projection are skipped."""
    # Query with valid and invalid projection fields
    filter_input: dict[str, object] = {
        "where": {"price": {"$lt": 100}},
        "fields": {"name": 1, "price": 1, "non_existent_field": 1},
    }

    ast: FilterAST = ASTBuilder().build(FilterNormalizer().normalize(FilterParser().parse(filter_input)))
    query, _projection_model, _ = engine.build_query(ast)
    results: list[Document] = await query.to_list()

    # Should return products under $100 with only name and price fields
    assert len(results) == 2
    for product in results:
        assert "name" in product
        assert "price" in product
