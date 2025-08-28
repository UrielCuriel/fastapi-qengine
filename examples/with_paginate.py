"""
Example FastAPI application demonstrating fastapi-qengine usage with fastapi-pagination.

Requirements:
- MongoDB running on localhost:27017
- fastapi-pagination installed: pip install fastapi-pagination

To start MongoDB locally:
- Using Docker: docker run -d -p 27017:27017 mongo:latest
- Or install MongoDB locally from https://www.mongodb.com/

To run this example:
- uv run python examples/with_paginate.py
- Then visit http://localhost:8502 for API documentation
"""

from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from beanie import Document, init_beanie
from fastapi import Depends, FastAPI
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.beanie import apaginate
from pymongo import AsyncMongoClient

from fastapi_qengine import create_qe_dependency, create_response_model, process_filter_to_ast
from fastapi_qengine.backends.beanie import BeanieQueryEngine, BeanieQueryResult


# Define Beanie models
class Product(Document):
    """Product model for demonstration."""

    name: str
    category: str
    price: float
    in_stock: bool
    tags: List[str] = []

    class Settings:
        name = "products"


ProductResponse = create_response_model(Product)

# FastAPI app


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database connection."""
    # For demo purposes - in production use proper connection string
    try:
        client = AsyncMongoClient("mongodb://localhost:27017")
        await init_beanie(database=client.demo_db, document_models=[Product])
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        print("Make sure MongoDB is running on localhost:27017")
        print("To start MongoDB with Docker: docker run -d -p 27017:27017 mongo:latest")
        raise

    # Insert sample data if collection is empty
    if await Product.count() == 0:
        sample_products = [
            Product(name="Laptop", category="electronics", price=999.99, in_stock=True, tags=["computer", "portable"]),
            Product(name="Mouse", category="electronics", price=29.99, in_stock=True, tags=["computer", "accessory"]),
            Product(name="Book", category="books", price=19.99, in_stock=False, tags=["education", "fiction"]),
            Product(
                name="Smartphone", category="electronics", price=699.99, in_stock=True, tags=["mobile", "communication"]
            ),
            Product(name="Coffee Mug", category="home", price=12.99, in_stock=True, tags=["kitchen", "ceramic"]),
            Product(name="Tablet", category="electronics", price=499.99, in_stock=True, tags=["computer", "portable"]),
            Product(name="Headphones", category="electronics", price=149.99, in_stock=True, tags=["audio", "wireless"]),
            Product(
                name="Keyboard", category="electronics", price=89.99, in_stock=False, tags=["computer", "accessory"]
            ),
            Product(name="Monitor", category="electronics", price=299.99, in_stock=True, tags=["computer", "display"]),
            Product(name="Chair", category="furniture", price=199.99, in_stock=True, tags=["office", "ergonomic"]),
            Product(name="Desk", category="furniture", price=349.99, in_stock=False, tags=["office", "wooden"]),
            Product(name="Lamp", category="home", price=59.99, in_stock=True, tags=["lighting", "LED"]),
            # Add more sample data for better pagination demonstration
        ]
        for i in range(20):
            sample_products.append(
                Product(
                    name=f"Product {i + 13}",
                    category="miscellaneous",
                    price=float(10 + i * 5),
                    in_stock=i % 2 == 0,
                    tags=["sample", "demo"],
                )
            )
        await Product.insert_many(sample_products)

    yield

    await Product.delete_all()
    await client.close()


app = FastAPI(title="fastapi-qengine with Pagination Demo", version="0.1.0", lifespan=lifespan)


# Create explicit engine and dependency
beanie_engine = BeanieQueryEngine(Product)
qe_dep = create_qe_dependency(beanie_engine)


@app.get("/products", response_model=Page[ProductResponse])
async def get_products_paginated(query_result: BeanieQueryResult = Depends(qe_dep)):
    """
    Get products with optional filtering and automatic pagination.

    Examples:

    Simple filters with pagination (nested params format):
    - /products?filter[where][category]=electronics&page=1&size=5
    - /products?filter[where][price][$gt]=50&page=2&size=3
    - /products?filter[where][in_stock]=true&filter[order]=-price&size=10

    Complex filters with pagination (JSON string format):
    - /products?filter={"where":{"$or":[{"category":"electronics"},{"price":{"$lt":20}}]}}&page=1&size=5
    - /products?filter={"where":{"price":{"$gte":10,"$lte":100}},"order":"name"}&size=8

    Pagination parameters:
    - page: Page number (1-based, default: 1)
    - size: Items per page (default: 50, max: 100)
    """
    # Extract the query result from fastapi-qengine
    beanie_query, projection_model, sort = query_result

    # Use fastapi-pagination's apaginate function with the Beanie query
    return await apaginate(
        beanie_query,
        projection_model=projection_model,
        sort=sort,
    )


@app.get("/products/search", response_model=Page[ProductResponse])
async def search_products_paginated(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    # programmatic route using explicit engine
):
    """
    Alternative endpoint showing programmatic query building with pagination.

    Examples:
    - /products/search?category=electronics&page=1&size=5
    - /products/search?min_price=10&max_price=100&size=10
    - /products/search?in_stock=true&category=electronics&page=2&size=3
    """
    # Build filter dictionary programmatically
    filter_dict: Dict[str, Any] = {"where": {}}

    if category:
        filter_dict["where"]["category"] = category

    if min_price is not None or max_price is not None:
        price_filter = {}
        if min_price is not None:
            price_filter["$gte"] = min_price
        if max_price is not None:
            price_filter["$lte"] = max_price
        filter_dict["where"]["price"] = price_filter

    if in_stock is not None:
        filter_dict["where"]["in_stock"] = in_stock

    # Process through pipeline and build query with engine
    if filter_dict["where"]:
        ast = process_filter_to_ast(filter_dict)
        beanie_query, projection_model, sort = beanie_engine.build_query(ast)
    else:
        # No filter - return all products
        beanie_query = Product.find()
        projection_model = None
        sort = None

    # Use fastapi-pagination's apaginate function
    return await apaginate(
        beanie_query,
        projection_model=projection_model,
        sort=sort,
    )


@app.get("/products/no-pagination", response_model=List[ProductResponse])
async def get_products_no_pagination(query_result=Depends(qe_dep)):
    """
    Get products without pagination (for comparison).
    Note: This endpoint doesn't use pagination and returns all matching results.
    """
    beanie_query, projection_model, sort = query_result

    # Apply projection if specified
    if projection_model:
        beanie_query = beanie_query.project(projection_model)

    # Apply sorting if specified
    if sort:
        beanie_query = beanie_query.sort(sort)

    products = await beanie_query.to_list()
    return products


@app.get("/")
async def root():
    """Root endpoint with usage examples."""
    return {
        "message": "fastapi-qengine with Pagination Demo API",
        "endpoints": {
            "/products": "Paginated products with filtering",
            "/products/search": "Programmatic search with pagination",
            "/products/no-pagination": "Products without pagination",
        },
        "examples": {
            "paginated_simple_filters": [
                "/products?filter[where][category]=electronics&page=1&size=5",
                "/products?filter[where][price][$gt]=50&page=2&size=3",
                "/products?filter[where][in_stock]=true&filter[order]=-price&size=10",
            ],
            "paginated_complex_filters": [
                '/products?filter={"where":{"$or":[{"category":"electronics"},{"price":{"$lt":20}}]}}&page=1&size=5',
                '/products?filter={"where":{"price":{"$gte":10,"$lte":100}},"order":"name"}&size=8',
            ],
            "programmatic_search": [
                "/products/search?category=electronics&page=1&size=5",
                "/products/search?min_price=10&max_price=100&size=10",
                "/products/search?in_stock=true&category=electronics&page=2&size=3",
            ],
            "pagination_params": {
                "page": "Page number (1-based, default: 1)",
                "size": "Items per page (default: 50, max: 100)",
            },
        },
        "features": [
            "Combines fastapi-qengine flexible filtering with fastapi-pagination",
            "Supports both URL parameter and JSON string filter formats",
            "Automatic pagination with page and size parameters",
            "Maintains all fastapi-qengine features (sorting, projection, etc.)",
            "Compatible with Beanie's native query system",
        ],
    }


# Add pagination support
add_pagination(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8502)
