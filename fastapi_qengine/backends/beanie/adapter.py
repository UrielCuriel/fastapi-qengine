"""
Beanie query adapter.

This module contains the BeanieQueryAdapter class for building Beanie/PyMongo queries.
"""

from typing import cast


class BeanieQueryAdapter:
    """Adapter for Beanie/PyMongo query objects."""

    def __init__(self):
        self.query: dict[str, object] = {}
        self.sort_spec: list[tuple[str, int]] = []
        self.projection: dict[str, int] | None = None

    def add_where_condition(self, condition: object) -> "BeanieQueryAdapter":
        """Add a where condition to the query."""
        condition = cast(dict[str, object], condition)
        if not self.query:
            self.query = condition
        else:
            # Merge with existing query using $and
            if "$and" in self.query:
                cast(list[object], self.query["$and"]).append(condition)
            else:
                self.query = {"$and": [self.query, condition]}
        return self

    def add_sort(self, field: str, ascending: bool = True) -> "BeanieQueryAdapter":
        """Add sorting to the query."""
        direction = 1 if ascending else -1
        self.sort_spec.append((field, direction))
        return self

    def set_projection(self, fields: dict[str, int]) -> "BeanieQueryAdapter":
        """Set field projection."""
        self.projection = fields
        return self

    def build(self) -> dict[str, object]:
        """Build the final query components."""
        result: dict[str, object] = {}

        if self.query:
            result["filter"] = self.query

        if self.sort_spec:
            result["sort"] = self.sort_spec

        if self.projection:
            result["projection"] = self.projection

        return result
