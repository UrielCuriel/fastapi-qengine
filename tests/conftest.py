"""
Pytest configuration and fixtures for fastapi-qengine tests.
"""

import asyncio
import uuid
from collections.abc import AsyncGenerator, Mapping

import pytest
import pytest_asyncio
from beanie import Document, init_beanie  # pyright: ignore[reportUnknownVariableType]
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import PyMongoError


@pytest.fixture
def sample_filter_data():
    """Sample filter data for tests."""
    return {
        "simple_equality": {"where": {"category": "electronics"}},
        "comparison_operators": {"where": {"price": {"$gt": 50, "$lte": 100}}},
        "logical_operators": {
            "where": {"$or": [{"category": "electronics"}, {"price": {"$lt": 20}}]}
        },
        "complex_query": {
            "where": {
                "$and": [
                    {"category": {"$in": ["electronics", "books"]}},
                    {"price": {"$gte": 10}},
                    {"$or": [{"in_stock": True}, {"tags": {"$in": ["featured"]}}]},
                ]
            },
            "order": "name,-price",
            "fields": {"name": 1, "price": 1, "category": 1},
        },
    }


@pytest.fixture
def sample_nested_params():
    """Sample nested parameter data for tests."""
    return {
        "simple": {
            "filter[where][category]": "electronics",
            "filter[where][price][$gt]": "50",
        },
        "with_order": {"filter[where][in_stock]": "true", "filter[order]": "-price"},
        "with_fields": {
            "filter[where][category]": "books",
            "filter[fields][name]": "1",
            "filter[fields][price]": "1",
        },
    }


@pytest.fixture
def sample_json_strings():
    """Sample JSON string filters for tests."""
    return {
        "simple": '{"where": {"category": "electronics"}}',
        "complex": '{"where": {"$or": [{"category": "electronics"}, {"price": {"$lt": 20}}]}, "order": "name"}',
        "with_fields": '{"where": {"price": {"$gte": 10}}, "fields": {"name": 1, "price": 1}}',
    }


# ============================================================================
# Beanie Integration Test Fixtures (Real MongoDB Connection)
# ============================================================================


@pytest_asyncio.fixture(scope="function")
async def db_name() -> str:
    """Genera un nombre de base de datos único para cada prueba.

    Returns:
        str: Nombre de la base de datos temporal.
    """
    return f"test_qengine_db_{uuid.uuid4().hex}"


@pytest_asyncio.fixture(scope="function")
async def mongo_client(
    db_name: str,
) -> AsyncGenerator[AsyncMongoClient[Mapping[str, object]], None]:
    """Crea un cliente Mongo local y espera disponibilidad con ping.

    Args:
        db_name: Nombre de la base de datos temporal.

    Yields:
        AsyncMongoClient: Cliente listo.
    """
    uri = "mongodb://localhost:27017"
    client = AsyncMongoClient[Mapping[str, object]](uri, appname="pytest-qengine")
    for attempt in range(10):
        try:
            _ = await client.admin.command({"ping": 1})
            break
        except PyMongoError:
            if attempt == 9:
                raise
            await asyncio.sleep(0.5 * (attempt + 1))
    yield client
    await client.drop_database(db_name)
    await client.close()


@pytest_asyncio.fixture(autouse=False, scope="function")
async def db_init(
    db_name: str, mongo_client: AsyncMongoClient[Mapping[str, object]]
) -> AsyncGenerator[None, None]:
    """Inicializa Beanie con los modelos de prueba.

    Args:
        db_name: Nombre de la base de datos temporal.
        mongo_client: Cliente de MongoDB.

    Yields:
        None
    """
    # Import test models here to avoid circular imports
    from tests.backends.test_beanie_security import SecureProduct, UserWithAddress

    modelos: list[type[Document]] = [SecureProduct, UserWithAddress]
    test_db: AsyncDatabase[Mapping[str, object]] = mongo_client.get_database(db_name)
    await init_beanie(database=test_db, document_models=modelos)
    yield
