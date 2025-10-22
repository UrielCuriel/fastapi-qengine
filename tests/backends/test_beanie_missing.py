"""
Tests for missing coverage in Beanie backend modules.
"""

import pytest

from fastapi_qengine.backends.beanie.adapter import BeanieQueryAdapter
from fastapi_qengine.backends.beanie.operators import (
    _register_beanie_comparison_operators,
    _register_beanie_custom_operators,
    _register_beanie_logical_operators,
    register_beanie_operators,
)
from fastapi_qengine.operators.base.registry import global_operator_registry


class TestBeanieQueryAdapter:
    """Test Beanie query adapter."""

    def test_adapter_initial_state(self):
        """Test adapter initial state."""
        adapter = BeanieQueryAdapter()

        assert adapter.query == {}
        assert adapter.sort_spec == []
        assert adapter.projection is None

    def test_add_where_condition_first(self):
        """Test adding first where condition."""
        adapter = BeanieQueryAdapter()
        adapter.add_where_condition({"name": "test"})

        assert adapter.query == {"name": "test"}

    def test_add_where_condition_merge_with_and(self):
        """Test merging multiple where conditions with $and."""
        adapter = BeanieQueryAdapter()
        adapter.add_where_condition({"name": "test"})
        adapter.add_where_condition({"category": "books"})

        assert "$and" in adapter.query
        assert len(adapter.query["$and"]) == 2

    def test_add_where_condition_append_to_existing_and(self):
        """Test appending to existing $and condition."""
        adapter = BeanieQueryAdapter()
        adapter.query = {"$and": [{"name": "test"}]}
        adapter.add_where_condition({"category": "books"})

        assert len(adapter.query["$and"]) == 2

    def test_add_sort_ascending(self):
        """Test adding ascending sort."""
        adapter = BeanieQueryAdapter()
        adapter.add_sort("name", True)

        assert adapter.sort_spec == [("name", 1)]

    def test_add_sort_descending(self):
        """Test adding descending sort."""
        adapter = BeanieQueryAdapter()
        adapter.add_sort("price", False)

        assert adapter.sort_spec == [("price", -1)]

    def test_add_multiple_sorts(self):
        """Test adding multiple sort specifications."""
        adapter = BeanieQueryAdapter()
        adapter.add_sort("name", True)
        adapter.add_sort("price", False)

        assert len(adapter.sort_spec) == 2
        assert adapter.sort_spec[0] == ("name", 1)
        assert adapter.sort_spec[1] == ("price", -1)

    def test_set_projection(self):
        """Test setting field projection."""
        adapter = BeanieQueryAdapter()
        adapter.set_projection({"name": 1, "price": 1})

        assert adapter.projection == {"name": 1, "price": 1}

    def test_build_empty(self):
        """Test building empty query."""
        adapter = BeanieQueryAdapter()
        result = adapter.build()

        assert result == {}

    def test_build_with_filter(self):
        """Test building query with filter."""
        adapter = BeanieQueryAdapter()
        adapter.add_where_condition({"name": "test"})
        result = adapter.build()

        assert "filter" in result
        assert result["filter"] == {"name": "test"}

    def test_build_with_sort(self):
        """Test building query with sort."""
        adapter = BeanieQueryAdapter()
        adapter.add_sort("name", True)
        result = adapter.build()

        assert "sort" in result
        assert result["sort"] == [("name", 1)]

    def test_build_with_projection(self):
        """Test building query with projection."""
        adapter = BeanieQueryAdapter()
        adapter.set_projection({"name": 1})
        result = adapter.build()

        assert "projection" in result
        assert result["projection"] == {"name": 1}

    def test_build_with_all_components(self):
        """Test building query with all components."""
        adapter = BeanieQueryAdapter()
        adapter.add_where_condition({"name": "test"})
        adapter.add_sort("price", False)
        adapter.set_projection({"name": 1, "price": 1})
        result = adapter.build()

        assert "filter" in result
        assert "sort" in result
        assert "projection" in result

    def test_adapter_method_chaining(self):
        """Test that adapter methods can be chained."""
        adapter = BeanieQueryAdapter()

        result = (
            adapter.add_where_condition({"name": "test"})
            .add_sort("price", False)
            .set_projection({"name": 1})
        )

        assert result is adapter


class TestBeanieOperators:
    """Test Beanie operator registrations."""

    def test_register_comparison_operators(self):
        """Test that comparison operators are registered."""
        # Operators are already registered when module is imported
        # Check that standard comparison operators are registered
        assert global_operator_registry.is_supported("$eq", backend="beanie")
        assert global_operator_registry.is_supported("$ne", backend="beanie")
        assert global_operator_registry.is_supported("$gt", backend="beanie")
        assert global_operator_registry.is_supported("$gte", backend="beanie")
        assert global_operator_registry.is_supported("$lt", backend="beanie")
        assert global_operator_registry.is_supported("$lte", backend="beanie")
        assert global_operator_registry.is_supported("$in", backend="beanie")
        assert global_operator_registry.is_supported("$nin", backend="beanie")
        assert global_operator_registry.is_supported("$regex", backend="beanie")
        assert global_operator_registry.is_supported("$exists", backend="beanie")
        assert global_operator_registry.is_supported("$size", backend="beanie")
        assert global_operator_registry.is_supported("$type", backend="beanie")

    def test_register_logical_operators(self):
        """Test that logical operators are registered."""
        assert global_operator_registry.is_supported("$and", backend="beanie")
        assert global_operator_registry.is_supported("$or", backend="beanie")
        assert global_operator_registry.is_supported("$nor", backend="beanie")

    def test_register_custom_operators(self):
        """Test that custom operators are registered."""
        assert global_operator_registry.is_supported("$text", backend="beanie")
        assert global_operator_registry.is_supported("$geoWithin", backend="beanie")
        assert global_operator_registry.is_supported("$near", backend="beanie")

    def test_register_all_beanie_operators(self):
        """Test that all operators are registered together."""
        # Verify a sample from each category
        assert global_operator_registry.is_supported("$eq", backend="beanie")
        assert global_operator_registry.is_supported("$and", backend="beanie")
        assert global_operator_registry.is_supported("$text", backend="beanie")

    def test_compile_eq_operator(self):
        """Test compiling $eq operator."""
        from fastapi_qengine.operators.base.registry import global_operator_registry

        compiler = global_operator_registry.get_compiler("$eq", backend="beanie")
        result = compiler("name", "test")

        assert result == {"name": "test"}

    def test_compile_ne_operator(self):
        """Test compiling $ne operator."""
        from fastapi_qengine.operators.base.registry import global_operator_registry

        compiler = global_operator_registry.get_compiler("$ne", backend="beanie")
        result = compiler("status", "inactive")

        assert result == {"status": {"$ne": "inactive"}}

    def test_compile_gt_operator(self):
        """Test compiling $gt operator."""
        from fastapi_qengine.operators.base.registry import global_operator_registry

        compiler = global_operator_registry.get_compiler("$gt", backend="beanie")
        result = compiler("price", 50)

        assert result == {"price": {"$gt": 50}}

    def test_compile_in_operator(self):
        """Test compiling $in operator."""
        from fastapi_qengine.operators.base.registry import global_operator_registry

        compiler = global_operator_registry.get_compiler("$in", backend="beanie")
        result = compiler("category", ["books", "electronics"])

        assert result == {"category": {"$in": ["books", "electronics"]}}

    def test_compile_regex_operator(self):
        """Test compiling $regex operator."""
        from fastapi_qengine.operators.base.registry import global_operator_registry

        compiler = global_operator_registry.get_compiler("$regex", backend="beanie")
        result = compiler("name", "^test.*")

        assert result == {"name": {"$regex": "^test.*"}}

    def test_compile_exists_operator(self):
        """Test compiling $exists operator."""
        from fastapi_qengine.operators.base.registry import global_operator_registry

        compiler = global_operator_registry.get_compiler("$exists", backend="beanie")
        result = compiler("optional_field", True)

        assert result == {"optional_field": {"$exists": True}}

    def test_compile_size_operator(self):
        """Test compiling $size operator."""
        from fastapi_qengine.operators.base.registry import global_operator_registry

        compiler = global_operator_registry.get_compiler("$size", backend="beanie")
        result = compiler("tags", 3)

        assert result == {"tags": {"$size": 3}}

    def test_compile_type_operator(self):
        """Test compiling $type operator."""
        from fastapi_qengine.operators.base.registry import global_operator_registry

        compiler = global_operator_registry.get_compiler("$type", backend="beanie")
        result = compiler("value", "string")

        assert result == {"value": {"$type": "string"}}

    def test_compile_and_operator(self):
        """Test compiling $and operator."""
        from fastapi_qengine.operators.base.registry import global_operator_registry

        compiler = global_operator_registry.get_compiler("$and", backend="beanie")
        conditions = [{"name": "test"}, {"category": "books"}]
        result = compiler(conditions)

        assert result == {"$and": conditions}

    def test_compile_or_operator(self):
        """Test compiling $or operator."""
        from fastapi_qengine.operators.base.registry import global_operator_registry

        compiler = global_operator_registry.get_compiler("$or", backend="beanie")
        conditions = [{"name": "test"}, {"category": "books"}]
        result = compiler(conditions)

        assert result == {"$or": conditions}

    def test_compile_nor_operator(self):
        """Test compiling $nor operator."""
        from fastapi_qengine.operators.base.registry import global_operator_registry

        compiler = global_operator_registry.get_compiler("$nor", backend="beanie")
        conditions = [{"name": "test"}, {"category": "books"}]
        result = compiler(conditions)

        assert result == {"$nor": conditions}

    def test_compile_text_operator(self):
        """Test compiling $text operator."""
        from fastapi_qengine.operators.base.registry import global_operator_registry

        compiler = global_operator_registry.get_compiler("$text", backend="beanie")
        result = compiler("_ignored_field_", "search term")

        assert result == {"$text": {"$search": "search term"}}

    def test_compile_geo_within_operator(self):
        """Test compiling $geoWithin operator."""
        from fastapi_qengine.operators.base.registry import global_operator_registry

        compiler = global_operator_registry.get_compiler("$geoWithin", backend="beanie")
        geo_data = {"$geometry": {"type": "Polygon", "coordinates": []}}
        result = compiler("location", geo_data)

        assert result == {"location": {"$geoWithin": geo_data}}

    def test_compile_near_operator(self):
        """Test compiling $near operator."""
        from fastapi_qengine.operators.base.registry import global_operator_registry

        compiler = global_operator_registry.get_compiler("$near", backend="beanie")
        geo_data = {"$geometry": {"type": "Point", "coordinates": [0, 0]}}
        result = compiler("location", geo_data)

        assert result == {"location": {"$near": geo_data}}
