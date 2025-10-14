"""
Example showing how to use security policies to control field access in queries.

Security policies allow you to:
1. Block sensitive fields from being queried or projected
2. Define a whitelist of allowed fields
3. Control field access in where clauses, order, and projection

This is useful for:
- Hiding sensitive data (passwords, internal costs, etc.)
- Creating different API access levels
- Implementing field-level permissions
"""

from typing import List

from beanie import Document, init_beanie
from fastapi import Depends, FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from fastapi_qengine import create_qe_dependency
from fastapi_qengine.backends.beanie import BeanieQueryEngine
from fastapi_qengine.core.response import create_response_model
from fastapi_qengine.core.types import SecurityPolicy

# ============================================================================
# Models
# ============================================================================


class Product(Document):
    """Product model with both public and internal fields."""

    name: str
    description: str
    price: float
    internal_cost: float  # Sensitive: should not be exposed to customers
    stock: int
    supplier_id: str  # Sensitive: internal reference
    is_active: bool
    category: str

    class Settings:
        name = "products"


# ============================================================================
# Security Policies
# ============================================================================

# Policy for public API - block sensitive fields
public_policy = SecurityPolicy(
    blocked_fields=["internal_cost", "supplier_id"],
    max_depth=5,
    max_array_size=100,
)

# Policy for internal/admin API - allow all fields
admin_policy = SecurityPolicy(
    max_depth=10,
    max_array_size=1000,
)

# Policy for minimal API - only allow specific fields
minimal_policy = SecurityPolicy(
    allowed_fields=["name", "price", "category"],
    max_depth=3,
    max_array_size=50,
)

# ============================================================================
# Query Engines with Policies
# ============================================================================

# Engine for public users - hides sensitive fields
public_engine = BeanieQueryEngine(Product, security_policy=public_policy)

# Engine for admin users - access to all fields
admin_engine = BeanieQueryEngine(Product, security_policy=admin_policy)

# Engine for limited API - only basic fields
minimal_engine = BeanieQueryEngine(Product, security_policy=minimal_policy)

# ============================================================================
# Response Models with Policies
# ============================================================================

# Create response models that respect security policies
PublicProductResponse = create_response_model(Product, security_policy=public_policy)
AdminProductResponse = create_response_model(Product, security_policy=admin_policy)
MinimalProductResponse = create_response_model(Product, security_policy=minimal_policy)

# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(title="Security Policies Example")

# Create dependencies with security policies
PublicQueryDep = create_qe_dependency(public_engine, security_policy=public_policy)
AdminQueryDep = create_qe_dependency(admin_engine, security_policy=admin_policy)
MinimalQueryDep = create_qe_dependency(minimal_engine, security_policy=minimal_policy)


@app.on_event("startup")
async def startup_db():
    """Initialize database connection."""
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    await init_beanie(database=client.products_db, document_models=[Product])


# ============================================================================
# Public Endpoints
# ============================================================================


@app.get("/products", response_model=List[PublicProductResponse])
async def list_products_public(query=Depends(PublicQueryDep)):
    """
    Public endpoint - sensitive fields are automatically blocked.

    Examples:
    - /products?filter={"where":{"price":{"$lt":100}}}
    - /products?filter={"where":{"category":"electronics"},"order":"price"}
    - /products?filter={"fields":{"name":1,"price":1}}

    Note: Attempts to query or project internal_cost or supplier_id will fail.
    """
    query_obj, projection_model, _ = query
    return await query_obj.to_list()


@app.get("/products/{product_id}", response_model=PublicProductResponse)
async def get_product_public(product_id: str):
    """Get single product - sensitive fields excluded."""
    product = await Product.get(product_id)
    return product


# ============================================================================
# Admin Endpoints
# ============================================================================


@app.get("/admin/products", response_model=List[AdminProductResponse])
async def list_products_admin(query=Depends(AdminQueryDep)):
    """
    Admin endpoint - access to all fields including sensitive data.

    Examples:
    - /admin/products?filter={"where":{"internal_cost":{"$lt":50}}}
    - /admin/products?filter={"fields":{"name":1,"internal_cost":1,"supplier_id":1}}
    """
    query_obj, projection_model, _ = query
    return await query_obj.to_list()


# ============================================================================
# Minimal API Endpoints
# ============================================================================


@app.get("/api/v1/products", response_model=List[MinimalProductResponse])
async def list_products_minimal(query=Depends(MinimalQueryDep)):
    """
    Minimal API - only basic fields (name, price, category).

    Examples:
    - /api/v1/products?filter={"where":{"category":"electronics"}}
    - /api/v1/products?filter={"fields":{"name":1,"price":1}}

    Note: Attempts to access other fields will fail.
    """
    query_obj, projection_model, _ = query
    return await query_obj.to_list()


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print("Security Policies Example")
    print("=" * 60)
    print()
    print("Public API (blocks internal_cost, supplier_id):")
    print("  GET /products")
    print()
    print("Admin API (allows all fields):")
    print("  GET /admin/products")
    print()
    print("Minimal API (only name, price, category):")
    print("  GET /api/v1/products")
    print()
    print("=" * 60)
    print()
    print("Example queries:")
    print()
    print("Public - Filter by price:")
    print('  /products?filter={"where":{"price":{"$lt":100}}}')
    print()
    print("Public - Try to access internal_cost (will fail):")
    print('  /products?filter={"where":{"internal_cost":{"$lt":50}}}')
    print()
    print("Admin - Access internal_cost:")
    print('  /admin/products?filter={"where":{"internal_cost":{"$lt":50}}}')
    print()
    print("Minimal - Only basic fields:")
    print('  /api/v1/products?filter={"fields":{"name":1,"price":1}}')
    print()
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000)
