"""
Tests for Beanie backend with security policies for field projection.
"""

import pytest
import pytest_asyncio
from beanie import Document
from pydantic import BaseModel

from fastapi_qengine.backends.beanie import BeanieQueryEngine
from fastapi_qengine.core.ast import ASTBuilder
from fastapi_qengine.core.normalizer import FilterNormalizer
from fastapi_qengine.core.parser import FilterParser
from fastapi_qengine.core.types import SecurityPolicy


class SecureProduct(Document):
    """Test model with sensitive fields."""

    name: str
    price: float
    internal_cost: float
    stock: int
    supplier_id: str
    is_active: bool

    class Settings:
        name: str = "secure_products"


class Address(BaseModel):
    """Address model for nested field tests."""

    street: str
    city: str
    secret_code: str


class UserWithAddress(Document):
    """User model with nested address."""

    name: str
    email: str
    address: Address

    class Settings:
        name: str = "users_with_address"


@pytest.mark.usefixtures("db_init")
class TestBeanieSecurityPolicyProjection:
    """Test Beanie query engine with security policies for projections."""

    @pytest_asyncio.fixture()
    async def parser(self):
        """Parser fixture."""
        return FilterParser()

    @pytest_asyncio.fixture()
    async def normalizer(self):
        """Normalizer fixture."""
        return FilterNormalizer()

    @pytest_asyncio.fixture()
    async def ast_builder(self):
        """AST builder fixture."""
        return ASTBuilder()

    @pytest.mark.asyncio
    async def test_projection_with_blocked_fields(
        self,
        parser: FilterParser,
        normalizer: FilterNormalizer,
        ast_builder: ASTBuilder,
    ):
        """Test that blocked fields are excluded from projection."""
        policy = SecurityPolicy(blocked_fields=["internal_cost", "supplier_id"])
        engine = BeanieQueryEngine(SecureProduct, security_policy=policy)

        # Request projection including blocked fields
        filter_str = (
            '{"fields": {"name": 1, "price": 1, "internal_cost": 1, "supplier_id": 1}}'
        )
        parsed = parser.parse(filter_str)
        normalized = normalizer.normalize(parsed)
        ast = ast_builder.build(normalized)

        _query, projection_model, _ = engine.build_query(ast)

        # Projection model should exist
        assert projection_model is not None

        # Check that blocked fields are not in the projection model
        assert "internal_cost" not in projection_model.model_fields
        assert "supplier_id" not in projection_model.model_fields

        # Allowed fields should be present
        assert "name" in projection_model.model_fields
        assert "price" in projection_model.model_fields

    @pytest.mark.asyncio
    async def test_projection_with_allowed_fields_only(
        self,
        parser: FilterParser,
        normalizer: FilterNormalizer,
        ast_builder: ASTBuilder,
    ):
        """Test that only allowed fields are included in projection."""
        policy = SecurityPolicy(allowed_fields=["name", "price", "stock"])
        engine = BeanieQueryEngine(SecureProduct, security_policy=policy)

        # Request projection with mix of allowed and non-allowed fields
        filter_str = (
            '{"fields": {"name": 1, "price": 1, "internal_cost": 1, "is_active": 1}}'
        )
        parsed = parser.parse(filter_str)
        normalized = normalizer.normalize(parsed)
        ast = ast_builder.build(normalized)

        _query, projection_model, _ = engine.build_query(ast)

        # Projection model should exist
        assert projection_model is not None

        # Only allowed fields should be in the projection model
        assert "name" in projection_model.model_fields
        assert "price" in projection_model.model_fields

        # Non-allowed fields should not be present
        assert "internal_cost" not in projection_model.model_fields
        assert "is_active" not in projection_model.model_fields

    @pytest.mark.asyncio
    async def test_projection_exclusion_mode_with_blocked_fields(
        self,
        parser: FilterParser,
        normalizer: FilterNormalizer,
        ast_builder: ASTBuilder,
    ):
        """Test exclusion mode respects blocked fields."""
        policy = SecurityPolicy(blocked_fields=["internal_cost", "supplier_id"])
        engine = BeanieQueryEngine(SecureProduct, security_policy=policy)

        # Use exclusion mode (all fields except specified)
        filter_str = '{"fields": {"price": 0}}'
        parsed = parser.parse(filter_str)
        normalized = normalizer.normalize(parsed)
        ast = ast_builder.build(normalized)

        _query, projection_model, _ = engine.build_query(ast)

        # Projection model should exist
        assert projection_model is not None

        # Excluded field should not be present
        assert "price" not in projection_model.model_fields

        # Blocked fields should also not be present even in exclusion mode
        assert "internal_cost" not in projection_model.model_fields
        assert "supplier_id" not in projection_model.model_fields

        # Other allowed fields should be present
        assert "name" in projection_model.model_fields
        assert "stock" in projection_model.model_fields
        assert "is_active" in projection_model.model_fields

    @pytest.mark.asyncio
    async def test_projection_with_allowed_and_blocked(
        self,
        parser: FilterParser,
        normalizer: FilterNormalizer,
        ast_builder: ASTBuilder,
    ):
        """Test that blocked fields take precedence over allowed fields."""
        policy = SecurityPolicy(
            allowed_fields=["name", "price", "internal_cost", "stock"],
            blocked_fields=["internal_cost"],
        )
        engine = BeanieQueryEngine(SecureProduct, security_policy=policy)

        # Request all fields that are in allowed list
        filter_str = (
            '{"fields": {"name": 1, "price": 1, "internal_cost": 1, "stock": 1}}'
        )
        parsed = parser.parse(filter_str)
        normalized = normalizer.normalize(parsed)
        ast = ast_builder.build(normalized)

        _query, projection_model, _ = engine.build_query(ast)

        # Projection model should exist
        assert projection_model is not None

        # internal_cost should be blocked even though it's in allowed list
        assert "internal_cost" not in projection_model.model_fields

        # Other allowed fields should be present
        assert "name" in projection_model.model_fields
        assert "price" in projection_model.model_fields
        assert "stock" in projection_model.model_fields

    @pytest.mark.asyncio
    async def test_projection_with_dot_notation_blocked_fields(
        self,
        parser: FilterParser,
        normalizer: FilterNormalizer,
        ast_builder: ASTBuilder,
    ):
        """Test that blocked fields work with dot notation."""
        policy = SecurityPolicy(blocked_fields=["address"])
        engine = BeanieQueryEngine(UserWithAddress, security_policy=policy)

        # Try to project address fields (should be blocked)
        filter_str = '{"fields": {"name": 1, "address.street": 1, "address.city": 1}}'
        parsed = parser.parse(filter_str)
        normalized = normalizer.normalize(parsed)
        ast = ast_builder.build(normalized)

        _query, projection_model, _ = engine.build_query(ast)

        # Projection model should exist with only allowed fields
        assert projection_model is not None

        # Name should be present
        assert "name" in projection_model.model_fields

        # Address and its nested fields should be blocked
        assert "address" not in projection_model.model_fields

    @pytest.mark.asyncio
    async def test_no_projection_when_all_blocked(
        self,
        parser: FilterParser,
        normalizer: FilterNormalizer,
        ast_builder: ASTBuilder,
    ):
        """Test that no projection model is created when all requested fields are blocked."""
        policy = SecurityPolicy(
            blocked_fields=[
                "name",
                "price",
                "internal_cost",
                "stock",
                "supplier_id",
                "is_active",
            ]
        )
        engine = BeanieQueryEngine(SecureProduct, security_policy=policy)

        # Request projection with only blocked fields
        filter_str = '{"fields": {"name": 1, "price": 1}}'
        parsed = parser.parse(filter_str)
        normalized = normalizer.normalize(parsed)
        ast = ast_builder.build(normalized)

        _query, projection_model, _ = engine.build_query(ast)

        # No projection model should be created
        assert projection_model is None

    @pytest.mark.asyncio
    async def test_projection_without_policy(
        self,
        parser: FilterParser,
        normalizer: FilterNormalizer,
        ast_builder: ASTBuilder,
    ):
        """Test that projection works normally without security policy."""
        engine = BeanieQueryEngine(SecureProduct)  # No security policy

        filter_str = '{"fields": {"name": 1, "price": 1, "internal_cost": 1}}'
        parsed = parser.parse(filter_str)
        normalized = normalizer.normalize(parsed)
        ast = ast_builder.build(normalized)

        _query, projection_model, _ = engine.build_query(ast)

        # Projection model should exist with all requested fields
        assert projection_model is not None
        assert "name" in projection_model.model_fields
        assert "price" in projection_model.model_fields
        assert "internal_cost" in projection_model.model_fields
