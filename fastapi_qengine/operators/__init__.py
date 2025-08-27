"""Operators module initialization."""

from .logical import LOGICAL_OPERATORS
from .comparison import COMPARISON_OPERATORS  
from .custom import (
    register_custom_operator, create_simple_operator,
    register_builtin_custom_operators, get_operator_handler,
    compile_operator
)

# Register built-in custom operators
register_builtin_custom_operators()

__all__ = [
    'LOGICAL_OPERATORS',
    'COMPARISON_OPERATORS',
    'register_custom_operator',
    'create_simple_operator', 
    'register_builtin_custom_operators',
    'get_operator_handler',
    'compile_operator',
]
