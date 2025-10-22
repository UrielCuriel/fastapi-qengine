"""
Advanced typing example for fastapi-qengine with multiple backends.

This example demonstrates:
1. How to properly type Engine instances for different backends
2. How to create type-safe dependencies
3. How to handle QueryResultType from different backends
4. Best practices for multi-backend applications
"""

from contextlib import asynccontextmanager
from typing import cast
from collections.abc import Mapping

from beanie import Document, init_beanie  # pyright: ignore[reportUnknownVariableType]
from fastapi import Depends, FastAPI
from pymongo import AsyncMongoClient
from pydantic import BaseModel

from fastapi_qengine import create_qe_dependency, process_filter_to_ast
from fastapi_qengine.backends.beanie import BeanieQueryEngine
from fastapi_qengine.backends.beanie.engine import BeanieQueryResult
from fastapi_qengine.core.types import Engine, FilterAST, QueryResultType, T


# ============================================================================
# 1. DEFINE YOUR PYDANTIC/BEANIE MODELS
# ============================================================================


class Product(Document):
    """Beanie Document model for products."""

    name: str
    price: float
    category: str
    in_stock: bool

    class Settings:
        name: str = "products"


class ProductBase(BaseModel):
    """Base schema for products (for responses)."""

    name: str
    price: float
    category: str
    in_stock: bool


class User(Document):
    """Beanie Document model for users."""

    username: str
    email: str
    is_active: bool

    class Settings:
        name: str = "users"


class UserBase(BaseModel):
    """Base schema for users (for responses)."""

    username: str
    email: str
    is_active: bool


# ============================================================================
# 2. CREATE TYPE-SAFE ENGINE INSTANCES
# ============================================================================

# Type: Engine[Product, BeanieQueryResult[Product]]
product_engine: Engine[Product, BeanieQueryResult[Product]] = BeanieQueryEngine(Product)

# Type: Engine[User, BeanieQueryResult[User]]
user_engine: Engine[User, BeanieQueryResult[User]] = BeanieQueryEngine(User)


# ============================================================================
# 3. CREATE TYPE-SAFE DEPENDENCIES
# ============================================================================

# Type: Callable[[Request, str | None], BeanieQueryResult[Product] | None]
product_query_dep = create_qe_dependency(product_engine)

# Type: Callable[[Request, str | None], BeanieQueryResult[User] | None]
user_query_dep = create_qe_dependency(user_engine)


# ============================================================================
# 4. HELPER FUNCTIONS DEMONSTRATING PROPER TYPING
# ============================================================================


def handle_query_result(
    query_result: BeanieQueryResult[Product] | None,
) -> tuple[object, object, object] | None:
    """
    Helper function showing proper type handling.

    Args:
        query_result: Result from the query dependency (can be None if no filter)

    Returns:
        Tuple of (query, projection_model, sort_spec) or None
    """
    if query_result is None:
        # No filter was provided
        return None

    # Unpack the tuple - type safety ensures these are correct types
    query, projection_model, sort_spec = query_result
    return query, projection_model, sort_spec


def handle_engine_agnostic(
    engine: Engine[T, QueryResultType], ast: FilterAST
) -> QueryResultType:
    """
    Generic function that works with any Engine implementation.

    This demonstrates how to write backend-agnostic code using the Engine protocol.

    Args:
        engine: Any Engine implementation (Beanie, SQLAlchemy, etc.)
        ast: The filter Abstract Syntax Tree

    Returns:
        Backend-specific QueryResultType
    """
    # This works with any backend because of the generic protocol
    return engine.build_query(ast)


# ============================================================================
# 5. FASTAPI APPLICATION WITH PROPER TYPING
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database connection."""
    _ = app
    client = AsyncMongoClient[Mapping[str, object]]("mongodb://localhost:27017")
    await init_beanie(database=client.demo_db, document_models=[Product, User])
    yield


app = FastAPI(
    title="fastapi-qengine Advanced Typing Example",
    version="0.1.0",
    lifespan=lifespan,
)


# ============================================================================
# 6. TYPE-SAFE ROUTE HANDLERS
# ============================================================================


@app.get("/products")
async def get_products(
    # Proper typing: explicitly declare the QueryResultType with | None
    query_result: BeanieQueryResult[Product] | None = Depends(product_query_dep),  # pyright: ignore[reportCallInDefaultInitializer]
) -> list[ProductBase]:
    """
    Get products with optional filtering.

    The type annotation shows:
    - BeanieQueryResult[Product]: The specific result type from Beanie backend
    - | None: The dependency returns None if no filter is provided
    """
    # Handle the None case
    if query_result is None:
        return cast(list[ProductBase], await Product.find_all().to_list())

    # Unpack the tuple with confidence (type checker validates this)
    query, projection_model, sort_spec = query_result

    # projection_model and sort_spec are available for advanced use cases
    # The query is properly typed by the type system
    _ = (projection_model, sort_spec)  # Mark as used for type checkers
    return cast(list[ProductBase], await query.to_list())


@app.get("/users")
async def get_users(
    # Same pattern, but for User model
    query_result: BeanieQueryResult[User] | None = Depends(user_query_dep),  # pyright: ignore[reportCallInDefaultInitializer]
) -> list[UserBase]:
    """
    Get users with optional filtering.

    Demonstrates that the same pattern works for different models.
    """
    if query_result is None:
        return cast(list[UserBase], await User.find_all().to_list())

    query, projection_model, sort_spec = query_result
    _ = (projection_model, sort_spec)  # Mark as used for type checkers
    return cast(list[UserBase], await query.to_list())


# ============================================================================
# 7. ADVANCED PATTERNS
# ============================================================================


@app.get("/products/advanced")
async def get_products_advanced(
    query_result: BeanieQueryResult[Product] | None = Depends(product_query_dep),  # pyright: ignore[reportCallInDefaultInitializer]
    limit: int = 10,
    skip: int = 0,
) -> dict[str, object]:
    """
    Advanced endpoint showing pagination with typed query results.
    """
    if query_result is None:
        total = await Product.count()
        products = await Product.find_all().skip(skip).limit(limit).to_list()
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": products,
        }

    query, projection_model, sort_spec = query_result
    _ = (projection_model, sort_spec)  # Mark as used for type checkers

    # Add pagination to the aggregation pipeline
    pipeline = query.aggregation_pipeline
    pipeline.extend([{"$skip": skip}, {"$limit": limit}])

    # Count total before pagination (simplified - could be used for total count)
    _ = pipeline[:-2] + [{"$count": "total"}]

    products = await query.to_list()
    total = await Product.count()  # Simplified for example

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": products,
    }


@app.post("/products/filter-and-transform")
async def filter_and_transform(
    filter_json: str,
) -> dict[str, object]:
    """
    Example showing programmatic use of the query engine with proper typing.

    This demonstrates:
    1. Manual AST creation
    2. Type-safe engine usage
    3. Result handling with proper types
    """
    # Parse and process the filter
    ast: FilterAST = process_filter_to_ast(filter_json)

    # Call engine with proper type inference
    query_result: BeanieQueryResult[Product] = product_engine.build_query(ast)

    query, projection_model, sort_spec = query_result
    _ = (projection_model, sort_spec)  # Mark as used for type checkers
    products = await query.to_list()

    return {
        "count": len(products),
        "items": products,
        "has_projection": projection_model is not None,
    }


# ============================================================================
# 8. MULTIPLE BACKEND SUPPORT (Future Pattern)
# ============================================================================

# When you add SQLAlchemy backend:
# from fastapi_qengine.backends.sqlalchemy import SQLAlchemyQueryEngine
# from fastapi_qengine.backends.sqlalchemy.engine import SQLAlchemyQueryResult
#
# sql_product_engine: Engine[Product, SQLAlchemyQueryResult[Product]] = (
#     SQLAlchemyQueryEngine(Product)
# )
#
# @app.get("/products/sql")
# async def get_products_sql(
#     query_result: SQLAlchemyQueryResult[Product] | None = Depends(
#         create_qe_dependency(sql_product_engine)
#     ),
# ) -> list[ProductBase]:
#     if query_result is None:
#         return session.query(Product).all()
#
#     select_stmt, projection_model = query_result
#     return session.execute(select_stmt).scalars().all()


@app.get("/")
async def root() -> dict[str, object]:
    """Root endpoint."""
    return {
        "message": "Advanced typing example for fastapi-qengine",
        "endpoints": {
            "simple_products": "/products",
            "simple_users": "/users",
            "advanced_products": "/products/advanced?limit=20&skip=0",
            "filter_and_transform": "/products/filter-and-transform",
        },
        "filter_examples": {
            "nested_params": "/products?filter[where][category]=electronics",
            "json_string": '/products?filter={"where":{"price":{"$gt":50}}}',
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8501)
