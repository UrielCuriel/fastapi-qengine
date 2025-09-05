"""
Pytest configuration and fixtures for fastapi-qengine tests.
"""

import asyncio
from typing import Generator

import pytest


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_filter_data():
    """Sample filter data for tests."""
    return {
        "simple_equality": {"where": {"category": "electronics"}},
        "comparison_operators": {"where": {"price": {"$gt": 50, "$lte": 100}}},
        "logical_operators": {"where": {"$or": [{"category": "electronics"}, {"price": {"$lt": 20}}]}},
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
        "simple": {"filter[where][category]": "electronics", "filter[where][price][$gt]": "50"},
        "with_order": {"filter[where][in_stock]": "true", "filter[order]": "-price"},
        "with_fields": {"filter[where][category]": "books", "filter[fields][name]": "1", "filter[fields][price]": "1"},
    }


@pytest.fixture
def sample_json_strings():
    """Sample JSON string filters for tests."""
    return {
        "simple": '{"where": {"category": "electronics"}}',
        "complex": '{"where": {"$or": [{"category": "electronics"}, {"price": {"$lt": 20}}]}, "order": "name"}',
        "with_fields": '{"where": {"price": {"$gte": 10}}, "fields": {"name": 1, "price": 1}}',
    }


class MockBeanieDocument:
    """Mock Beanie document for testing."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def find(cls, filter_dict=None):
        """Mock find method."""
        return MockBeanieQuery(filter_dict or {})

    @classmethod
    def find_all(cls):
        """Mock find_all method."""
        return MockBeanieQuery({})


class MockBeanieQuery:
    """Mock Beanie query for testing."""

    def __init__(self, filter_dict):
        self.filter_dict = filter_dict
        self.sort_spec = []
        self.projection_spec = {}

    def sort(self, sort_spec):
        """Mock sort method."""
        self.sort_spec = sort_spec
        return self

    def project(self, **projection):
        """Mock project method."""
        self.projection_spec = projection
        return self

    def to_list(self):
        """Mock to_list method."""
        return [
            MockBeanieDocument(name="Test Product", category="electronics", price=99.99),
            MockBeanieDocument(name="Another Product", category="books", price=19.99),
        ]


@pytest.fixture
def mock_beanie_model():
    """Mock Beanie model for testing."""
    return MockBeanieDocument
