"""
Tests for the base query compiler.
"""

from typing import cast

import pytest

from fastapi_qengine.core.compiler_base import (
    BaseQueryCompiler,
    QueryAdapter,
    compile_condition_helper,
)
from fastapi_qengine.core.errors import CompilerError
from fastapi_qengine.core.types import (
    ASTNode,
    ComparisonOperator,
    FieldCondition,
    FieldsNode,
    FilterAST,
    LogicalCondition,
    LogicalOperator,
    OrderNode,
)


class MockQueryAdapter(QueryAdapter):
    """Mock query adapter for testing."""

    def __init__(self):
        self.where_conditions: list[object] = []
        self.order_by: list[tuple[str, str]] = []
        self.fields: dict[str, int] | None = None

    def add_where_condition(self, condition: object) -> QueryAdapter:
        self.where_conditions.append(condition)
        return cast(QueryAdapter, self)

    def add_sort(self, field: str, ascending: bool = True) -> QueryAdapter:
        self.order_by.append((field, "asc" if ascending else "desc"))
        return cast(QueryAdapter, self)

    def set_projection(self, fields: dict[str, int]) -> QueryAdapter:
        self.fields = fields
        return cast(QueryAdapter, self)

    def build(self) -> dict[str, object]:
        return {
            "where": self.where_conditions,
            "order": self.order_by,
            "fields": self.fields,
        }


class MockQueryCompiler(BaseQueryCompiler):
    """Mock query compiler for testing."""

    def __init__(self, backend_name: str):
        self.backend_name = backend_name

    def compile(self, ast: FilterAST) -> dict[str, object]:
        """Compile FilterAST to a dictionary representation."""
        adapter = self.create_base_query()

        if ast.where is not None:
            adapter = self.apply_where(adapter, ast.where)

        if ast.order is not None:
            adapter = self.apply_order(adapter, ast.order)

        if ast.fields is not None:
            adapter = self.apply_fields(adapter, ast.fields)

        return adapter.build()

    def compile_condition(self, condition: ASTNode) -> object:
        """Compile a condition using the helper function."""
        return compile_condition_helper(self, condition)

    def create_base_query(self) -> QueryAdapter:
        return MockQueryAdapter()

    def apply_where(self, query: QueryAdapter, where_node: ASTNode) -> QueryAdapter:
        condition = self.compile_condition(where_node)
        return query.add_where_condition(condition)

    def apply_order(self, query: QueryAdapter, order_nodes: list[OrderNode]) -> QueryAdapter:
        for node in order_nodes:
            query.add_sort(node.field, node.ascending)
        return query

    def apply_fields(self, query: QueryAdapter, fields_node: FieldsNode) -> QueryAdapter:
        return query.set_projection(fields_node.fields)

    def finalize_query(self, query: QueryAdapter):
        return query.build()

    def compile_field_condition(self, condition: FieldCondition) -> str:
        return f"{condition.field} {condition.operator.value} {condition.value}"

    def compile_logical_condition(self, condition: LogicalCondition) -> dict:
        return {
            condition.operator.value: [self.compile_condition(c) for c in condition.conditions],
        }


def test_base_compiler_compile():
    """Test the main compile method of the base compiler."""
    ast = FilterAST(
        where=LogicalCondition(
            operator=LogicalOperator.AND,
            conditions=[
                FieldCondition(field="name", operator=ComparisonOperator.EQ, value="test"),
                FieldCondition(field="age", operator=ComparisonOperator.GT, value=10),
            ],
        ),
        order=[OrderNode(field="name", ascending=True)],
        fields=FieldsNode(fields={"name": 1}),
    )

    compiler = MockQueryCompiler("mock")

    result = compiler.compile(ast)

    assert result["where"] == [{"$and": ["name $eq test", "age $gt 10"]}]
    assert result["order"] == [("name", "asc")]
    assert result["fields"] == {"name": 1}


def test_compile_unknown_node_type():
    """Test that compiling an unknown AST node type raises an error."""
    compiler = MockQueryCompiler("mock")

    class UnknownNode(ASTNode):
        pass

    with pytest.raises(CompilerError, match="Unknown condition type"):
        compiler.compile_condition(UnknownNode())


def test_compiler_with_empty_ast():
    """Test the compiler with an empty AST."""
    compiler = MockQueryCompiler("mock")
    ast = FilterAST(where=None, order=None, fields=None)
    result = compiler.compile(ast)
    assert result["where"] == []
    assert result["order"] == []
    assert result["fields"] is None
