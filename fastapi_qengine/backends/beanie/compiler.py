"""
Beanie query compiler.

This module contains the BeanieQueryCompiler class for compiling queries to Beanie/PyMongo format.
"""

from typing import cast

from ...core.compiler_base import QueryAdapter, compile_condition_helper
from ...core.errors import CompilerError
from ...core.types import (
    ASTNode,
    FieldCondition,
    FieldsNode,
    FilterAST,
    LogicalCondition,
    OrderNode,
)
from ...operators.base.registry import (
    ComparisonCompiler,
    LogicalCompiler,
    global_operator_registry,
)
from .adapter import BeanieQueryAdapter


class BeanieQueryCompiler:
    """Query compiler for Beanie/PyMongo backend."""

    def __init__(self):
        self.backend_name: str = "beanie"
        self.adapter: BeanieQueryAdapter | None = None

    def create_base_query(self) -> BeanieQueryAdapter:
        """Create the base query adapter for Beanie."""
        self.adapter = BeanieQueryAdapter()
        return self.adapter

    def apply_where(self, query: QueryAdapter, where_node: ASTNode) -> QueryAdapter:
        """Apply where conditions to the query."""
        condition = self.compile_condition(where_node)
        return query.add_where_condition(condition)

    def apply_order(
        self, query: QueryAdapter, order_nodes: list[OrderNode]
    ) -> QueryAdapter:
        """Apply ordering to the query."""
        for order_node in order_nodes:
            query = query.add_sort(order_node.field, order_node.ascending)
        return query

    def apply_fields(
        self, query: QueryAdapter, fields_node: FieldsNode
    ) -> QueryAdapter:
        """Apply field projection to the query."""
        return query.set_projection(fields_node.fields)

    def finalize_query(self, query: QueryAdapter) -> dict[str, object]:
        """Finalize the query and return MongoDB query components."""
        return cast(dict[str, object], query.build())

    def compile_field_condition(self, condition: FieldCondition) -> dict[str, object]:
        """Compile a field condition to MongoDB format."""
        compiler: ComparisonCompiler | None = cast(
            ComparisonCompiler,
            global_operator_registry.get_compiler(
                condition.operator.value, self.backend_name
            ),
        )
        if not compiler:
            raise CompilerError(f"Unsupported operator: {condition.operator}")

        return compiler(condition.field, condition.value)

    def compile_logical_condition(
        self, condition: LogicalCondition
    ) -> dict[str, list[object]]:
        """Compile a logical condition to MongoDB format."""
        compiler: LogicalCompiler = cast(
            LogicalCompiler,
            global_operator_registry.get_compiler(
                condition.operator.value, self.backend_name
            ),
        )
        if not compiler:
            raise CompilerError(f"Unsupported logical operator: {condition.operator}")

        # Compile nested conditions
        compiled_conditions = [
            self.compile_condition(nested_condition)
            for nested_condition in condition.conditions
        ]

        return compiler(compiled_conditions)

    def compile_condition(self, condition: ASTNode) -> object:
        """Compile a condition node to backend-specific format."""
        return compile_condition_helper(self, condition)

    def supports_backend(self, backend_type: str) -> bool:
        """Check if this compiler supports the given backend."""
        return backend_type == self.backend_name

    def compile(self, ast: FilterAST) -> dict[str, object]:
        """
        Compile FilterAST to MongoDB query components.

        Args:
            ast: FilterAST to compile

        Returns:
            Dictionary with query components (filter, sort, projection)
        """
        query = self.create_base_query()

        # Apply where conditions
        if ast.where:
            query = self.apply_where(query, ast.where)

        # Apply ordering
        if ast.order:
            query = self.apply_order(query, ast.order)

        # Apply field projection
        if ast.fields:
            query = self.apply_fields(query, ast.fields)

        return self.finalize_query(query)
