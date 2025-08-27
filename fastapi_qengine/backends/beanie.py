"""
Beanie/PyMongo backend compiler.
"""
from typing import Any, Dict, List, Optional, Union

from ..core.compiler_base import BaseQueryCompiler, QueryAdapter
from ..core.types import (
    FilterAST, ASTNode, FieldCondition, LogicalCondition, OrderNode, FieldsNode,
    ComparisonOperator, LogicalOperator
)
from ..core.errors import CompilerError
from ..operators.comparison import COMPARISON_OPERATORS
from ..operators.logical import LOGICAL_OPERATORS


class BeanieQueryAdapter(QueryAdapter):
    """Adapter for Beanie/PyMongo query objects."""
    
    def __init__(self):
        self.query: Dict[str, Any] = {}
        self.sort_spec: List[tuple] = []
        self.projection: Optional[Dict[str, int]] = None
    
    def add_where_condition(self, condition: Dict[str, Any]) -> 'BeanieQueryAdapter':
        """Add a where condition to the query."""
        if not self.query:
            self.query = condition
        else:
            # Merge with existing query using $and
            if '$and' in self.query:
                self.query['$and'].append(condition)
            else:
                self.query = {'$and': [self.query, condition]}
        return self
    
    def add_sort(self, field: str, ascending: bool = True) -> 'BeanieQueryAdapter':
        """Add sorting to the query."""
        direction = 1 if ascending else -1
        self.sort_spec.append((field, direction))
        return self
    
    def set_projection(self, fields: Dict[str, int]) -> 'BeanieQueryAdapter':
        """Set field projection."""
        self.projection = fields
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build the final query components."""
        result = {}
        
        if self.query:
            result['filter'] = self.query
        
        if self.sort_spec:
            result['sort'] = self.sort_spec
        
        if self.projection:
            result['projection'] = self.projection
        
        return result


class BeanieQueryCompiler(BaseQueryCompiler):
    """Query compiler for Beanie/PyMongo backend."""
    
    def __init__(self):
        super().__init__("beanie")
        self.adapter: Optional[BeanieQueryAdapter] = None
    
    def create_base_query(self) -> BeanieQueryAdapter:
        """Create the base query adapter for Beanie."""
        self.adapter = BeanieQueryAdapter()
        return self.adapter
    
    def apply_where(self, query: BeanieQueryAdapter, where_node: ASTNode) -> BeanieQueryAdapter:
        """Apply where conditions to the query."""
        condition = self.compile_condition(where_node)
        return query.add_where_condition(condition)
    
    def apply_order(self, query: BeanieQueryAdapter, order_nodes: List[OrderNode]) -> BeanieQueryAdapter:
        """Apply ordering to the query."""
        for order_node in order_nodes:
            query.add_sort(order_node.field, order_node.ascending)
        return query
    
    def apply_fields(self, query: BeanieQueryAdapter, fields_node: FieldsNode) -> BeanieQueryAdapter:
        """Apply field projection to the query."""
        return query.set_projection(fields_node.fields)
    
    def finalize_query(self, query: BeanieQueryAdapter) -> Dict[str, Any]:
        """Finalize the query and return MongoDB query components."""
        return query.build()
    
    def compile_field_condition(self, condition: FieldCondition) -> Dict[str, Any]:
        """Compile a field condition to MongoDB format."""
        handler = COMPARISON_OPERATORS.get(condition.operator)
        if not handler:
            raise CompilerError(f"Unsupported operator: {condition.operator}")
        
        return handler.compile(condition.field, condition.value, self.backend_name)
    
    def compile_logical_condition(self, condition: LogicalCondition) -> Dict[str, Any]:
        """Compile a logical condition to MongoDB format."""
        handler = LOGICAL_OPERATORS.get(condition.operator)
        if not handler:
            raise CompilerError(f"Unsupported logical operator: {condition.operator}")
        
        # Compile nested conditions
        compiled_conditions = [
            self.compile_condition(nested_condition) 
            for nested_condition in condition.conditions
        ]
        
        return handler.compile(compiled_conditions, self.backend_name)


class BeanieQueryEngine:
    """High-level query engine for Beanie models."""
    
    def __init__(self, model_class):
        """
        Initialize query engine for a Beanie model.
        
        Args:
            model_class: Beanie Document class
        """
        self.model_class = model_class
        self.compiler = BeanieQueryCompiler()
    
    def build_query(self, ast: FilterAST):
        """
        Build a Beanie query from FilterAST.
        
        Args:
            ast: FilterAST to compile
            
        Returns:
            Beanie query object
        """
        query_components = self.compiler.compile(ast)
        
        # Start with base find query
        query = self.model_class.find()
        
        # Apply filter
        if 'filter' in query_components:
            query = self.model_class.find(query_components['filter'])
        
        # Apply sort
        if 'sort' in query_components:
            query = query.sort(query_components['sort'])
        
        # Apply projection
        if 'projection' in query_components:
            query = query.project(**query_components['projection'])
        
        return query
    
    def execute_query(self, ast: FilterAST):
        """
        Execute query and return results.
        
        Args:
            ast: FilterAST to execute
            
        Returns:
            Query results
        """
        query = self.build_query(ast)
        return query


# Convenience function for creating MongoDB queries directly
def compile_to_mongodb(ast: FilterAST) -> Dict[str, Any]:
    """
    Compile FilterAST directly to MongoDB query components.
    
    Args:
        ast: FilterAST to compile
        
    Returns:
        Dict with 'filter', 'sort', and/or 'projection' keys
    """
    compiler = BeanieQueryCompiler()
    return compiler.compile(ast)
