"""
FastAPI Query Engine - Advanced filtering for FastAPI applications.

A powerful query engine inspired by Loopback 4's filtering system,
providing flexible URL-based filtering with support for complex queries,
operators, and automatic OpenAPI documentation generation.
"""

from .backends.beanie import create_beanie_dependency
from .core.config import QEngineConfig, SecurityPolicy
from .core.errors import ParseError, QEngineError, SecurityError, ValidationError
from .core.types import ComparisonOperator, FilterAST, FilterCondition, LogicalOperator
from .dependency import QueryEngine
from .openapi_schema import FilterSchemaGenerator, generate_filter_docs

__version__ = "0.1.0"

__all__ = [
    # Main components
    "QueryEngine",
    "create_beanie_dependency",
    # Core types
    "FilterAST",
    "FilterCondition",
    "LogicalOperator",
    "ComparisonOperator",
    # Configuration
    "QEngineConfig",
    "SecurityPolicy",
    # Errors
    "QEngineError",
    "ParseError",
    "ValidationError",
    "SecurityError",
    # OpenAPI documentation
    "generate_filter_docs",
    "FilterSchemaGenerator",
]

__version__ = "0.1.0"

# Core imports
# Backend-specific imports
from .backends import BeanieQueryEngine, compile_to_mongodb
from .core import (
    FilterAST,
    FilterInput,
    ParseError,
    QEngineConfig,
    QEngineError,
    SecurityError,
    SecurityPolicy,
    ValidationError,
    default_config,
)

# Main interface
from .dependency import create_beanie_dependency, create_pymongo_dependency

# Operator utilities
from .operators import create_simple_operator, register_custom_operator

__all__ = [
    # Version
    "__version__",
    # Main interface
    "QueryEngine",
    "create_beanie_dependency",
    "create_pymongo_dependency",
    # Core types
    "FilterAST",
    "FilterInput",
    "QEngineConfig",
    "SecurityPolicy",
    "default_config",
    # Errors
    "QEngineError",
    "ParseError",
    "ValidationError",
    "SecurityError",
    # Backend utilities
    "BeanieQueryEngine",
    "compile_to_mongodb",
    # Operator utilities
    "register_custom_operator",
    "create_simple_operator",
]


def main():
    print("fastapi-qengine: Advanced query engine for FastAPI")
    print(f"Version: {__version__}")
    print("For usage examples, see: https://github.com/yourusername/fastapi-qengine")


if __name__ == "__main__":
    main()
