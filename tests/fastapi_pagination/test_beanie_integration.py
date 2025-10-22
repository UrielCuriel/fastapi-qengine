# pyright: basic
"""
Integration tests for fastapi-qengine with fastapi-pagination.

Tests cover:
- Query building with nested URL parameter format
- Query building with JSON string format
- Programmatic query construction
- Field projection and sorting
- Complex queries with logical operators
- Integration with fastapi-pagination's apaginate function
"""

from collections.abc import AsyncGenerator, Mapping

import pytest_asyncio
from beanie import Document, init_beanie
from fastapi import FastAPI
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate
from httpx import ASGITransport, AsyncClient
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from fastapi_qengine import process_filter_to_ast
from fastapi_qengine.backends.beanie import BeanieQueryEngine


# Define Beanie model for testing
class Product(Document):
    """Product model for testing."""

    name: str
    category: str
    price: float
    in_stock: bool
    tags: list[str] = []

    class Settings:
        name: str = "products"


@pytest_asyncio.fixture(autouse=True)
async def pagination_setup():
    """Set up pagination params for tests."""
    from fastapi_pagination import set_params
    from fastapi_pagination.limit_offset import LimitOffsetParams

    set_params(LimitOffsetParams())
    yield


@pytest_asyncio.fixture(scope="function")
async def db_init_with_products(
    db_name: str, mongo_client: AsyncMongoClient[Mapping[str, object]]
) -> AsyncGenerator[AsyncDatabase[Mapping[str, object]], None]:
    """Initialize Beanie with Product model and sample data."""
    test_db: AsyncDatabase[Mapping[str, object]] = mongo_client.get_database(db_name)
    await init_beanie(database=test_db, document_models=[Product])

    # Insert sample products
    sample_products = [
        Product(
            name="Laptop",
            category="electronics",
            price=999.99,
            in_stock=True,
            tags=["computer", "portable"],
        ),
        Product(
            name="Mouse",
            category="electronics",
            price=29.99,
            in_stock=True,
            tags=["computer", "accessory"],
        ),
        Product(
            name="Book",
            category="books",
            price=19.99,
            in_stock=False,
            tags=["education", "fiction"],
        ),
        Product(
            name="Smartphone",
            category="electronics",
            price=699.99,
            in_stock=True,
            tags=["mobile", "communication"],
        ),
        Product(
            name="Coffee Mug",
            category="home",
            price=12.99,
            in_stock=True,
            tags=["kitchen", "ceramic"],
        ),
        Product(
            name="Tablet",
            category="electronics",
            price=499.99,
            in_stock=True,
            tags=["computer", "portable"],
        ),
        Product(
            name="Headphones",
            category="electronics",
            price=149.99,
            in_stock=True,
            tags=["audio", "wireless"],
        ),
        Product(
            name="Keyboard",
            category="electronics",
            price=89.99,
            in_stock=False,
            tags=["computer", "accessory"],
        ),
        Product(
            name="Monitor",
            category="electronics",
            price=299.99,
            in_stock=True,
            tags=["computer", "display"],
        ),
        Product(
            name="Chair",
            category="furniture",
            price=199.99,
            in_stock=True,
            tags=["office", "ergonomic"],
        ),
    ]

    await Product.insert_many(sample_products)
    yield test_db

    # Cleanup: clear all collections
    for collection_name in await test_db.list_collection_names():
        await test_db[collection_name].delete_many({})


@pytest_asyncio.fixture
async def engine(db_init_with_products: AsyncDatabase[Mapping[str, object]]) -> BeanieQueryEngine[Product]:
    """Create a Beanie query engine instance."""
    return BeanieQueryEngine(Product)


class TestBasicFilteringWithPagination:
    """Tests for basic filtering with fastapi-pagination integration."""

    async def test_filter_by_category_with_pagination(self, engine: BeanieQueryEngine[Product]) -> None:
        """Test filtering by category with pagination."""
        filter_dict: dict[str, object] = {"where": {"category": "electronics"}}
        ast = process_filter_to_ast(filter_dict)
        query, _projection_model, _sort = engine.build_query(ast)

        # Use apaginate for pagination
        page_result: Page[Product] = await apaginate(query)  # pyright: ignore[reportAny]

        # Verify pagination structure
        assert hasattr(page_result, "items")
        assert hasattr(page_result, "total")
        assert len(page_result.items) <= page_result.total

        # Should have 7 electronics products
        assert page_result.total == 7
        for product in page_result.items:
            assert product.category == "electronics"

    async def test_filter_by_price_greater_than_with_pagination(self, engine: BeanieQueryEngine[Product]) -> None:
        """Test filtering with $gt operator and pagination."""
        filter_dict: dict[str, object] = {"where": {"price": {"$gt": 500}}}
        ast = process_filter_to_ast(filter_dict)
        query, _projection_model, _sort = engine.build_query(ast)

        page_result: Page[Product] = await apaginate(query)  # pyright: ignore[reportAny]

        # Verify pagination and filtering
        assert page_result.total > 0
        for product in page_result.items:
            assert product.price > 500

    async def test_filter_by_stock_status_with_pagination(self, engine: BeanieQueryEngine[Product]) -> None:
        """Test filtering by stock status with pagination."""
        filter_dict: dict[str, object] = {"where": {"in_stock": True}}
        ast = process_filter_to_ast(filter_dict)
        query, _projection_model, _sort = engine.build_query(ast)

        page_result: Page[Product] = await apaginate(query)  # pyright: ignore[reportAny]

        # Verify all items are in stock
        assert page_result.total > 0
        for product in page_result.items:
            assert product.in_stock is True

    async def test_complex_filter_with_or_and_pagination(self, engine: BeanieQueryEngine[Product]) -> None:
        """Test complex filtering with OR operator and pagination."""
        filter_dict: dict[str, object] = {"where": {"$or": [{"category": "electronics"}, {"price": {"$lt": 20}}]}}
        ast = process_filter_to_ast(filter_dict)
        query, _projection_model, _sort = engine.build_query(ast)

        page_result: Page[Product] = await apaginate(query)  # pyright: ignore[reportAny]

        # Should have electronics products or products under $20
        assert page_result.total > 0
        for product in page_result.items:
            is_electronics = product.category == "electronics"
            is_cheap = product.price < 20
            assert is_electronics or is_cheap


class TestSortingWithPagination:
    """Tests for sorting functionality with fastapi-pagination."""

    async def test_sort_by_price_ascending_with_pagination(self, engine: BeanieQueryEngine[Product]) -> None:
        """Test sorting by price in ascending order with pagination."""
        filter_dict: dict[str, object] = {"order": "price"}
        ast = process_filter_to_ast(filter_dict)
        query, _projection_model, sort = engine.build_query(ast)

        page_result: Page[Product] = await apaginate(query, sort=sort)  # pyright: ignore[reportAny]

        # Verify pagination structure and items
        assert page_result.total > 0
        assert len(page_result.items) > 1

        # Verify items are sorted by price ascending
        for i in range(len(page_result.items) - 1):
            assert page_result.items[i].price <= page_result.items[i + 1].price

    async def test_sort_by_price_descending_with_pagination(self, engine: BeanieQueryEngine[Product]) -> None:
        """Test sorting by price in descending order with pagination."""
        filter_dict: dict[str, object] = {"order": "-price"}
        ast = process_filter_to_ast(filter_dict)
        query, _projection_model, sort = engine.build_query(ast)

        page_result: Page[Product] = await apaginate(query, sort=sort)  # pyright: ignore[reportAny]

        # Verify pagination and sorting
        assert page_result.total > 0
        assert len(page_result.items) > 1

        # Verify items are sorted by price descending
        for i in range(len(page_result.items) - 1):
            assert page_result.items[i].price >= page_result.items[i + 1].price

    async def test_sort_by_name_with_filter_and_pagination(self, engine: BeanieQueryEngine[Product]) -> None:
        """Test sorting by name with category filter and pagination."""
        filter_dict: dict[str, object] = {
            "where": {"category": "electronics"},
            "order": "name",
        }
        ast = process_filter_to_ast(filter_dict)
        query, _projection_model, sort = engine.build_query(ast)

        page_result: Page[Product] = await apaginate(query, sort=sort)  # pyright: ignore[reportAny]

        # Verify pagination, filtering, and sorting
        assert page_result.total == 7

        # Verify items are filtered
        for product in page_result.items:
            assert product.category == "electronics"

        # Verify sorted by name
        if len(page_result.items) > 1:
            for i in range(len(page_result.items) - 1):
                assert page_result.items[i].name <= page_result.items[i + 1].name


class TestProjectionWithPagination:
    """Tests for field projection with fastapi-pagination."""

    async def test_field_projection_with_pagination(self, engine: BeanieQueryEngine[Product]) -> None:
        """Test selecting specific fields with pagination."""
        filter_dict: dict[str, object] = {"fields": {"name": 1, "price": 1}}
        ast = process_filter_to_ast(filter_dict)
        query, _, _sort = engine.build_query(ast)

        page_result: Page[dict] = await apaginate(query)  # pyright: ignore[reportAny]

        # Verify pagination structure
        assert page_result.total > 0
        assert len(page_result.items) > 0

        # The projection should constrain output to specified fields
        for product in page_result.items:
            assert "name" in product
            assert "price" in product

    async def test_field_projection_with_filter_and_pagination(self, engine: BeanieQueryEngine[Product]) -> None:
        """Test field projection combined with filtering and pagination."""
        filter_dict: dict[str, object] = {
            "where": {"category": "electronics"},
            "fields": {"name": 1, "category": 1},
        }
        ast = process_filter_to_ast(filter_dict)
        query, _, _sort = engine.build_query(ast)

        page_result: Page[dict] = await apaginate(query)  # pyright: ignore[reportAny]

        # Verify pagination and filtering
        assert page_result.total == 7
        for product in page_result.items:
            assert product["category"] == "electronics"
            assert "name" in product
            assert "category" in product


class TestProgrammaticQueryBuildingWithPagination:
    """Tests for programmatic query construction with pagination."""

    async def test_search_by_category_with_pagination(self, engine: BeanieQueryEngine[Product]) -> None:
        """Test programmatic search by category with pagination."""
        filter_dict: dict[str, object] = {"where": {"category": "electronics"}}
        ast = process_filter_to_ast(filter_dict)
        query, _projection_model, _sort = engine.build_query(ast)

        page_result: Page[Product] = await apaginate(query)  # pyright: ignore[reportAny]

        # Should have electronics products
        assert page_result.total == 7
        for product in page_result.items:
            assert product.category == "electronics"

    async def test_search_by_price_range_with_pagination(self, engine: BeanieQueryEngine[Product]) -> None:
        """Test programmatic search by price range with pagination."""
        filter_dict: dict[str, object] = {"where": {"price": {"$gte": 50, "$lte": 200}}}
        ast = process_filter_to_ast(filter_dict)
        query, _projection_model, _sort = engine.build_query(ast)

        page_result: Page[Product] = await apaginate(query)  # pyright: ignore[reportAny]

        # Verify pagination and filtering
        assert page_result.total > 0
        for product in page_result.items:
            assert 50 <= product.price <= 200

    async def test_search_by_stock_status_with_pagination(self, engine: BeanieQueryEngine[Product]) -> None:
        """Test programmatic search by stock status with pagination."""
        filter_dict: dict[str, object] = {"where": {"in_stock": True}}
        ast = process_filter_to_ast(filter_dict)
        query, _projection_model, _sort = engine.build_query(ast)

        page_result: Page[Product] = await apaginate(query)  # pyright: ignore[reportAny]

        # Verify pagination and filtering
        assert page_result.total > 0
        for product in page_result.items:
            assert product.in_stock is True

    async def test_search_combined_filters_with_pagination(self, engine: BeanieQueryEngine[Product]) -> None:
        """Test programmatic search with multiple filters and pagination."""
        filter_dict: dict[str, object] = {
            "where": {
                "category": "electronics",
                "in_stock": True,
                "price": {"$gte": 100},
            }
        }
        ast = process_filter_to_ast(filter_dict)
        query, _projection_model, _sort = engine.build_query(ast)

        page_result: Page[Product] = await apaginate(query)  # pyright: ignore[reportAny]

        # Verify pagination and all filters are applied
        assert page_result.total > 0
        for product in page_result.items:
            assert product.category == "electronics"
            assert product.in_stock is True
            assert product.price >= 100

    async def test_search_no_results_with_pagination(self, engine: BeanieQueryEngine[Product]) -> None:
        """Test search that returns no results with pagination."""
        filter_dict: dict[str, object] = {"where": {"price": {"$gte": 10000, "$lte": 20000}}}
        ast = process_filter_to_ast(filter_dict)
        query, _projection_model, _sort = engine.build_query(ast)

        page_result: Page[Product] = await apaginate(query)  # pyright: ignore[reportAny]

        # Should return empty results
        assert page_result.total == 0
        assert len(page_result.items) == 0


class TestComplexQueriesWithPagination:
    """Tests for complex query scenarios combining multiple features with pagination."""

    async def test_complex_query_with_all_features_and_pagination(self, engine: BeanieQueryEngine[Product]) -> None:
        """Test query combining filtering, sorting, and projection with pagination."""
        filter_dict: dict[str, object] = {
            "where": {"$or": [{"category": "electronics"}, {"price": {"$lt": 20}}]},
            "order": "-price",
            "fields": {"name": 1, "price": 1, "category": 1},
        }
        ast = process_filter_to_ast(filter_dict)
        query, _, sort = engine.build_query(ast)

        page_result: Page[dict] = await apaginate(query, sort=sort)  # pyright: ignore[reportAny]

        # Verify pagination structure
        assert page_result.total > 0
        assert len(page_result.items) > 0

        # Verify filtering logic
        for product in page_result.items:
            is_electronics = product["category"] == "electronics"
            is_cheap = product["price"] < 20
            assert is_electronics or is_cheap

        # Verify sorting
        if len(page_result.items) > 1:
            for i in range(len(page_result.items) - 1):
                assert page_result.items[i]["price"] >= page_result.items[i + 1]["price"]

    async def test_nested_logical_operators_with_pagination(self, engine: BeanieQueryEngine[Product]) -> None:
        """Test queries with nested AND/OR logic and pagination."""
        filter_dict: dict[str, object] = {
            "where": {
                "$and": [
                    {"$or": [{"category": "electronics"}, {"category": "furniture"}]},
                    {"in_stock": True},
                ]
            }
        }
        ast = process_filter_to_ast(filter_dict)
        query, _projection_model, _sort = engine.build_query(ast)

        page_result: Page[Product] = await apaginate(query)  # pyright: ignore[reportAny]

        # Verify pagination and filtering
        assert page_result.total > 0
        for product in page_result.items:
            is_target_category = product.category in ["electronics", "furniture"]
            assert is_target_category and product.in_stock is True

    async def test_multiple_conditions_same_field_with_pagination(self, engine: BeanieQueryEngine[Product]) -> None:
        """Test multiple conditions on the same field with pagination."""
        filter_dict: dict[str, object] = {"where": {"price": {"$gte": 100, "$lte": 500}}}
        ast = process_filter_to_ast(filter_dict)
        query, _projection_model, _sort = engine.build_query(ast)

        page_result: Page[Product] = await apaginate(query)  # pyright: ignore[reportAny]

        # Verify pagination and filtering
        assert page_result.total > 0
        for product in page_result.items:
            assert 100 <= product.price <= 500


class TestPaginationPageBoundaries:
    """Tests for pagination boundaries and edge cases."""

    async def test_pagination_default_page_size(self, engine: BeanieQueryEngine[Product]) -> None:
        """Test pagination with default page size."""
        filter_dict: dict[str, object] = {"where": {"category": "electronics"}}
        ast = process_filter_to_ast(filter_dict)
        query, _projection_model, _sort = engine.build_query(ast)

        # Request first page with default page size
        page_result: Page[Product] = await apaginate(query)  # pyright: ignore[reportAny]

        # Verify pagination structure
        assert hasattr(page_result, "items")
        assert hasattr(page_result, "total")
        assert page_result.total == 7

    async def test_pagination_with_custom_page_size(self, engine: BeanieQueryEngine[Product]) -> None:
        """Test pagination with custom page sizes."""
        from fastapi_pagination.limit_offset import LimitOffsetParams

        filter_dict: dict[str, object] = {"where": {"category": "electronics"}}
        ast = process_filter_to_ast(filter_dict)
        query, _projection_model, _sort = engine.build_query(ast)

        # Request with small page size
        params = LimitOffsetParams(limit=2, offset=0)
        page_result: Page[Product] = await apaginate(query, params=params)  # pyright: ignore[reportAny]

        # Verify pagination works with custom size
        assert page_result.total == 7
        assert len(page_result.items) <= 2

    async def test_pagination_total_matches_all_items(self, engine: BeanieQueryEngine[Product]) -> None:
        """Test that pagination total count is accurate."""
        filter_dict: dict[str, object] = {"where": {"in_stock": True}}
        ast = process_filter_to_ast(filter_dict)
        query, _projection_model, _sort = engine.build_query(ast)

        page_result: Page[Product] = await apaginate(query)  # pyright: ignore[reportAny]

        # Verify total is accurate
        assert page_result.total > 0
        assert len(page_result.items) <= page_result.total

    async def test_pagination_with_complex_filter_total(self, engine: BeanieQueryEngine[Product]) -> None:
        """Test pagination total count with complex filters."""
        filter_dict: dict[str, object] = {
            "where": {
                "$or": [
                    {"category": "electronics", "in_stock": True},
                    {"category": "furniture", "price": {"$lt": 250}},
                ]
            }
        }
        ast = process_filter_to_ast(filter_dict)
        query, _projection_model, _sort = engine.build_query(ast)

        page_result: Page[Product] = await apaginate(query)  # pyright: ignore[reportAny]

        # Verify pagination structure with complex query
        assert page_result.total > 0
        assert len(page_result.items) <= page_result.total


class TestFastAPIAppIntegration:
    """Tests for full FastAPI app integration with fastapi-pagination."""

    def _build_search_filter(
        self,
        category: str | None,
        min_price: float | None,
        max_price: float | None,
        in_stock: bool | None,
    ) -> dict[str, object]:
        """Build search filter dictionary."""
        filter_dict: dict[str, object] = {"where": {}}
        where_clause = filter_dict.setdefault("where", {})
        if not isinstance(where_clause, dict):
            where_clause = {}
            filter_dict["where"] = where_clause

        if category:
            where_clause["category"] = category

        if min_price is not None or max_price is not None:
            price_filter: dict[str, object] = {}
            if min_price is not None:
                price_filter["$gte"] = min_price
            if max_price is not None:
                price_filter["$lte"] = max_price
            where_clause["price"] = price_filter

        if in_stock is not None:
            where_clause["in_stock"] = in_stock

        return filter_dict

    @pytest_asyncio.fixture
    async def fastapi_app(self) -> AsyncGenerator:  # type: ignore[type-arg]  # noqa: C901
        """Create a FastAPI app with pagination support."""
        from contextlib import asynccontextmanager

        from fastapi import Depends
        from fastapi_pagination import add_pagination

        from fastapi_qengine import create_qe_dependency, create_response_model
        from fastapi_qengine.backends.beanie import BeanieQueryEngine, BeanieQueryResult

        # Use the Product model from this test module
        product_response = create_response_model(Product)

        @asynccontextmanager
        async def lifespan(app: FastAPI):  # type: ignore[name-defined]
            """Lifespan context manager."""
            yield

        app = FastAPI(
            title="fastapi-qengine with Pagination Test",
            version="0.1.0",
            lifespan=lifespan,
        )

        # Create engine
        beanie_engine = BeanieQueryEngine(Product)
        qe_dep = create_qe_dependency(beanie_engine)
        test_self = self

        @app.get("/products", response_model=Page[product_response])  # type: ignore[valid-type]
        async def get_products_paginated() -> Page[Product]:  # type: ignore[name-defined]
            """Get paginated products with filtering support."""
            beanie_query = Product.find()  # type: ignore[attr-defined]
            return await apaginate(beanie_query)  # pyright: ignore[reportAny]

        @app.get("/products/filtered", response_model=Page[product_response])  # type: ignore[valid-type]
        async def get_products_filtered(
            query_result: BeanieQueryResult[Product] | None = Depends(qe_dep),  # pyright: ignore[reportCallInDefaultInitializer]  # type: ignore[name-defined,arg-type]
        ) -> Page[Product]:  # type: ignore[name-defined]
            """Get paginated products with fastapi-qengine filtering."""
            if query_result:
                beanie_query, _projection_model, sort = query_result
            else:
                beanie_query = Product.find()  # type: ignore[attr-defined]
                sort = None

            return await apaginate(beanie_query, sort=sort)  # pyright: ignore[reportAny]

        @app.get("/products/search", response_model=Page[product_response])  # type: ignore[valid-type]
        async def search_products_paginated(
            category: str | None = None,
            min_price: float | None = None,
            max_price: float | None = None,
            in_stock: bool | None = None,
        ) -> Page[Product]:  # type: ignore[name-defined]
            """Programmatic search with pagination."""
            filter_dict = test_self._build_search_filter(category, min_price, max_price, in_stock)
            where_clause = filter_dict.get("where", {})

            if where_clause:
                ast = process_filter_to_ast(filter_dict)  # type: ignore[arg-type]
                beanie_query, _projection_model, sort = beanie_engine.build_query(ast)
            else:
                beanie_query = Product.find()
                sort = None

            return await apaginate(beanie_query, sort=sort)  # pyright: ignore[reportAny]

        # Add pagination support to the app
        add_pagination(app)

        yield app

    @pytest_asyncio.fixture
    async def http_client(
        self, fastapi_app: FastAPI, db_init_with_products: AsyncDatabase[Mapping[str, object]]
    ) -> AsyncGenerator:  # type: ignore[type-arg]
        """Create HTTP test client for FastAPI app."""
        transport = ASGITransport(app=fastapi_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client

    async def test_fastapi_app_basic_pagination_endpoint(
        self,
        http_client: AsyncClient,  # type: ignore[type-arg]
    ) -> None:
        """Test basic pagination endpoint response structure."""
        response = await http_client.get("/products")

        assert response.status_code == 200
        data = response.json()

        # Verify pagination response structure
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data

        # Verify items are Product objects
        assert isinstance(data["items"], list)
        assert len(data["items"]) > 0
        assert data["total"] > 0

    async def test_fastapi_app_pagination_with_default_page_size(
        self,
        http_client: AsyncClient,  # type: ignore[type-arg]
    ) -> None:
        """Test pagination endpoint with default page size."""
        response = await http_client.get("/products?page=1&size=5")

        assert response.status_code == 200
        data = response.json()

        # Verify pagination metadata
        assert data["page"] == 1
        assert data["size"] == 5
        assert len(data["items"]) <= 5

    async def test_fastapi_app_pagination_multiple_pages(
        self,
        http_client: AsyncClient,  # type: ignore[type-arg]
    ) -> None:
        """Test pagination across multiple pages."""
        # Get first page
        response1 = await http_client.get("/products?page=1&size=2")
        assert response1.status_code == 200
        data1 = response1.json()

        # Get second page
        response2 = await http_client.get("/products?page=2&size=2")
        assert response2.status_code == 200
        data2 = response2.json()

        # Verify different items on different pages
        if data1["total"] > 2:
            assert data1["items"] != data2["items"]

    async def test_fastapi_app_filtered_products_with_pagination(
        self,
        http_client: AsyncClient,  # type: ignore[type-arg]
    ) -> None:
        """Test filtering endpoint with pagination."""
        response = await http_client.get("/products/filtered?filter[where][category]=electronics")

        assert response.status_code == 200
        data = response.json()

        # Verify pagination structure
        assert "items" in data
        assert "total" in data

        # Verify filtered results
        for item in data["items"]:
            assert item["category"] == "electronics"

    async def test_fastapi_app_programmatic_search_with_pagination(
        self,
        http_client: AsyncClient,  # type: ignore[type-arg]
    ) -> None:
        """Test programmatic search endpoint with pagination."""
        response = await http_client.get(
            "/products/search?category=electronics&in_stock=true&min_price=50&max_price=500"
        )

        assert response.status_code == 200
        data = response.json()

        # Verify pagination structure
        assert "items" in data
        assert "total" in data

        # Verify all filters are applied in results
        for item in data["items"]:
            assert item["category"] == "electronics"
            assert item["in_stock"] is True
            assert 50 <= item["price"] <= 500

    async def test_fastapi_app_search_no_results_pagination(
        self,
        http_client: AsyncClient,  # type: ignore[type-arg]
    ) -> None:
        """Test search with no results returns empty paginated response."""
        response = await http_client.get("/products/search?min_price=10000&max_price=20000")

        assert response.status_code == 200
        data = response.json()

        # Verify empty pagination
        assert data["total"] == 0
        assert len(data["items"]) == 0
        assert "page" in data
        assert "size" in data

    async def test_fastapi_app_pagination_response_structure(
        self,
        http_client: AsyncClient,  # type: ignore[type-arg]
    ) -> None:
        """Test complete pagination response structure."""
        response = await http_client.get("/products?page=1&size=3")

        assert response.status_code == 200
        data = response.json()

        # Verify all pagination fields
        required_fields = ["items", "total", "page", "size"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        # Verify field types
        assert isinstance(data["items"], list)
        assert isinstance(data["total"], int)
        assert isinstance(data["page"], int)
        assert isinstance(data["size"], int)

        # Verify logical consistency
        assert data["page"] >= 1
        assert data["size"] >= 1
        assert len(data["items"]) <= data["size"]
        assert data["total"] >= len(data["items"])

    async def test_fastapi_app_pagination_last_page(
        self,
        http_client: AsyncClient,  # type: ignore[type-arg]
    ) -> None:
        """Test pagination on the last page."""
        # Get total count first
        response_first = await http_client.get("/products?page=1&size=5")
        data_first = response_first.json()
        total = data_first["total"]

        # Calculate last page
        last_page = (total + 4) // 5  # Size is 5

        # Get last page
        response_last = await http_client.get(f"/products?page={last_page}&size=5")
        assert response_last.status_code == 200
        data_last = response_last.json()

        # Verify last page has remaining items
        assert len(data_last["items"]) > 0
        assert len(data_last["items"]) <= 5

    async def test_fastapi_app_pagination_with_complex_filter(
        self,
        http_client: AsyncClient,  # type: ignore[type-arg]
    ) -> None:
        """Test pagination with complex filtering."""
        response = await http_client.get(
            '/products/filtered?filter={"where":{"$or":[{"category":"electronics"},{"price":{"$lt":20}}]}}'
        )

        assert response.status_code == 200
        data = response.json()

        # Verify pagination structure
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data

        # Verify filtering logic
        for item in data["items"]:
            is_electronics = item["category"] == "electronics"
            is_cheap = item["price"] < 20
            assert is_electronics or is_cheap
