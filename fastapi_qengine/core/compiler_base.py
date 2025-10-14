"""
Base compiler class and interfaces.
"""

from typing import Protocol

from .errors import CompilerError
from .types import (
    ASTNode,
    FieldCondition,
    FieldsNode,
    LogicalCondition,
    OrderNode,
)


class QueryAdapter(Protocol):
    """Protocol for different query adapter types."""

    def add_where_condition(self, condition: object) -> "QueryAdapter":
        """Add a where condition to the query."""
        ...

    def add_sort(self, field: str, ascending: bool = True) -> "QueryAdapter":
        """Add sorting to the query."""
        ...

    def set_projection(self, fields: dict[str, int]) -> "QueryAdapter":
        """Set field projection."""
        ...

    def build(self) -> object:
        """Build the final query object."""
        ...


class BaseQueryCompiler(Protocol):
    """Protocol for query compilers implementing Template Method pattern."""

    backend_name: str

    def create_base_query(self) -> QueryAdapter:
        """Create the base query object for this backend."""
        ...

    def apply_where(self, query: QueryAdapter, where_node: ASTNode) -> QueryAdapter:
        """Apply where conditions to the query."""
        ...

    def apply_order(
        self, query: QueryAdapter, order_nodes: list[OrderNode]
    ) -> QueryAdapter:
        """Apply ordering to the query."""
        ...

    def apply_fields(
        self, query: QueryAdapter, fields_node: FieldsNode
    ) -> QueryAdapter:
        """Apply field projection to the query."""
        ...

    def compile_field_condition(self, condition: FieldCondition) -> object:
        """Compile a field condition to backend-specific format."""
        ...

    def compile_logical_condition(self, condition: LogicalCondition) -> object:
        """Compile a logical condition to backend-specific format."""
        ...

    def finalize_query(self, query: QueryAdapter) -> object:
        """Finalize the query before returning (default: return as-is)."""
        ...

    def supports_backend(self, backend_type: str) -> bool:
        """Check if this compiler supports the given backend."""
        ...

    def compile_condition(self, condition: ASTNode) -> object:
        """Compile a condition node to backend-specific format."""
        ...


# Helper function for compile_condition to be used by implementations
def compile_condition_helper(compiler: BaseQueryCompiler, condition: ASTNode) -> object:
    """Helper function to compile a condition node to backend-specific format."""
    if isinstance(condition, FieldCondition):
        return compiler.compile_field_condition(condition)
    elif isinstance(condition, LogicalCondition):
        return compiler.compile_logical_condition(condition)
    else:
        raise CompilerError(f"Unknown condition type: {type(condition)}")
