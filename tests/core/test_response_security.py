"""
Tests for response model creation with security policies.
"""

from typing import cast
import pytest
from pydantic import BaseModel

from fastapi_qengine.core.response import create_response_model
from fastapi_qengine.core.types import SecurityPolicy


class User(BaseModel):
    """Test model for user with sensitive fields."""

    id: int
    username: str
    email: str
    password_hash: str
    is_admin: bool
    created_at: str


class TestResponseModelSecurityPolicy:
    """Test response model creation with security policies."""

    def test_create_response_model_without_policy(self):
        """Test creating response model without security policy."""
        ResponseModel = create_response_model(User)

        # All fields should be present and optional
        assert "id" in ResponseModel.model_fields
        assert "username" in ResponseModel.model_fields
        assert "email" in ResponseModel.model_fields
        assert "password_hash" in ResponseModel.model_fields
        assert "is_admin" in ResponseModel.model_fields
        assert "created_at" in ResponseModel.model_fields

        # Test instantiation
        instance: User = cast(User, ResponseModel())
        assert instance.id is None
        assert instance.username is None  # pyright: ignore[reportUnreachable]

    def test_create_response_model_with_blocked_fields(self):
        """Test creating response model with blocked fields."""
        policy = SecurityPolicy(blocked_fields=["password_hash", "is_admin"])
        ResponseModel = create_response_model(User, security_policy=policy)

        # Blocked fields should not be present
        assert "password_hash" not in ResponseModel.model_fields
        assert "is_admin" not in ResponseModel.model_fields

        # Other fields should be present
        assert "id" in ResponseModel.model_fields
        assert "username" in ResponseModel.model_fields
        assert "email" in ResponseModel.model_fields
        assert "created_at" in ResponseModel.model_fields

    def test_create_response_model_with_allowed_fields(self):
        """Test creating response model with allowed fields whitelist."""
        policy = SecurityPolicy(allowed_fields=["id", "username", "email"])
        ResponseModel = create_response_model(User, security_policy=policy)

        # Only allowed fields should be present
        assert "id" in ResponseModel.model_fields
        assert "username" in ResponseModel.model_fields
        assert "email" in ResponseModel.model_fields

        # Other fields should not be present
        assert "password_hash" not in ResponseModel.model_fields
        assert "is_admin" not in ResponseModel.model_fields
        assert "created_at" not in ResponseModel.model_fields

    def test_create_response_model_with_allowed_and_blocked(self):
        """Test that blocked_fields takes precedence over allowed_fields."""
        # Even if in allowed list, blocked fields should be excluded
        policy = SecurityPolicy(
            allowed_fields=["id", "username", "email", "password_hash"],
            blocked_fields=["password_hash"],
        )
        ResponseModel = create_response_model(User, security_policy=policy)

        # password_hash should be blocked even though it's in allowed list
        assert "password_hash" not in ResponseModel.model_fields

        # Other allowed fields should be present
        assert "id" in ResponseModel.model_fields
        assert "username" in ResponseModel.model_fields
        assert "email" in ResponseModel.model_fields

        # Fields not in allowed list should not be present
        assert "is_admin" not in ResponseModel.model_fields
        assert "created_at" not in ResponseModel.model_fields

    def test_create_response_model_all_fields_blocked(self):
        """Test that error is raised when all fields are blocked."""
        policy = SecurityPolicy(
            blocked_fields=[
                "id",
                "username",
                "email",
                "password_hash",
                "is_admin",
                "created_at",
            ]
        )

        with pytest.raises(
            ValueError, match="Security policy resulted in no available fields"
        ):
            _ = create_response_model(User, security_policy=policy)

    def test_create_response_model_empty_allowed_fields(self):
        """Test that error is raised when allowed_fields is empty."""
        policy = SecurityPolicy(allowed_fields=[])

        with pytest.raises(
            ValueError, match="Security policy resulted in no available fields"
        ):
            _ = create_response_model(User, security_policy=policy)

    def test_create_response_model_with_data(self):
        """Test that response model can be instantiated with data respecting policy."""
        policy = SecurityPolicy(blocked_fields=["password_hash"])
        ResponseModel = create_response_model(User, security_policy=policy)

        # Create instance with partial data
        instance = cast(
            User, ResponseModel(id=1, username="testuser", email="test@example.com")
        )

        assert instance.id == 1
        assert instance.username == "testuser"
        assert instance.email == "test@example.com"
        assert instance.is_admin is None  # Not provided, should be None
        assert instance.created_at is None

        # password_hash should not exist
        assert not hasattr(instance, "password_hash")


class Product(BaseModel):
    """Test model for product."""

    id: int
    name: str
    price: float
    internal_cost: float
    stock: int
    supplier_id: str


class TestResponseModelWithProduct:
    """Test response model creation with product model."""

    def test_hide_sensitive_pricing_info(self):
        """Test hiding internal cost information."""
        policy = SecurityPolicy(blocked_fields=["internal_cost", "supplier_id"])
        ResponseModel = create_response_model(Product, security_policy=policy)

        # Public fields should be present
        assert "id" in ResponseModel.model_fields
        assert "name" in ResponseModel.model_fields
        assert "price" in ResponseModel.model_fields
        assert "stock" in ResponseModel.model_fields

        # Sensitive fields should be blocked
        assert "internal_cost" not in ResponseModel.model_fields
        assert "supplier_id" not in ResponseModel.model_fields

    def test_public_api_fields_only(self):
        """Test exposing only public API fields."""
        policy = SecurityPolicy(allowed_fields=["id", "name", "price"])
        ResponseModel = create_response_model(Product, security_policy=policy)

        # Only public API fields should be present
        assert "id" in ResponseModel.model_fields
        assert "name" in ResponseModel.model_fields
        assert "price" in ResponseModel.model_fields

        # Internal fields should not be exposed
        assert "internal_cost" not in ResponseModel.model_fields
        assert "supplier_id" not in ResponseModel.model_fields
        assert "stock" not in ResponseModel.model_fields
