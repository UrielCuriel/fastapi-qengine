"""
Example FastAPI application demonstrating fastapi-qengine usage.
"""

from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from beanie import Document, init_beanie
from fastapi import Depends, FastAPI
from pymongo import AsyncMongoClient

from fastapi_qengine import create_qe_dependency, create_response_model, process_filter_to_ast
from fastapi_qengine.backends.beanie import BeanieQueryCompiler, BeanieQueryEngine, BeanieQueryResult


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
    client = AsyncMongoClient("mongodb://localhost:27017")
    await init_beanie(database=client.demo_db, document_models=[Product])

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
        ]
        await Product.insert_many(sample_products)

    yield


app = FastAPI(title="fastapi-qengine Demo", version="0.1.0", lifespan=lifespan)


# Create explicit backend engine and dependency
beanie_engine = BeanieQueryEngine(Product)
qe_dep = create_qe_dependency(beanie_engine)


@app.get("/products", response_model=List[ProductResponse], response_model_exclude_none=True)
async def get_products(query_result: BeanieQueryResult = Depends(qe_dep)):
    """
    Get products with optional filtering.

    Examples:

    Simple filters (nested params format):
    - /products?filter[where][category]=electronics
    - /products?filter[where][price][$gt]=50
    - /products?filter[where][in_stock]=true&filter[order]=-price

    Complex filters (JSON string format):
    - /products?filter={"where":{"$or":[{"category":"electronics"},{"price":{"$lt":20}}]}}
    - /products?filter={"where":{"price":{"$gte":10,"$lte":100}},"order":"name"}
    """
    query, _, _ = query_result
    if query:
        products = await query.to_list()
    else:
        # No filter - return all products
        products = await Product.find_all().to_list()

    return products


@app.get("/products/search")
async def search_products(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    # Using explicit engine + pipeline helpers (no dependency)
):
    """
    Alternative endpoint showing programmatic query building.
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

    # Process through core pipeline and compile for Beanie/MongoDB
    if filter_dict["where"]:
        ast = process_filter_to_ast(filter_dict)
        mongo = BeanieQueryCompiler().compile(ast)
        products = await Product.find(mongo.get("filter", {})).to_list()
    else:
        products = await Product.find_all().to_list()

    return products


@app.get("/")
async def root():
    """Root endpoint with usage examples."""
    return {
        "message": "fastapi-qengine Demo API",
        "examples": {
            "simple_filters": [
                "/products?filter[where][category]=electronics",
                "/products?filter[where][price][$gt]=50",
                "/products?filter[where][in_stock]=true&filter[order]=-price",
            ],
            "complex_filters": [
                '/products?filter={"where":{"$or":[{"category":"electronics"},{"price":{"$lt":20}}]}}',
                '/products?filter={"where":{"price":{"$gte":10,"$lte":100}},"order":"name"}',
            ],
            "programmatic": "/products/search?category=electronics&min_price=10&max_price=1000",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8500)
