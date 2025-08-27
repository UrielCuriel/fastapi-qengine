"""Core module initialization."""

from .types import *
from .errors import *
from .config import *
from .parser import FilterParser
from .normalizer import FilterNormalizer
from .validator import FilterValidator
from .ast import ASTBuilder
from .optimizer import ASTOptimizer
from .registry import compiler_registry, operator_registry
from .compiler_base import BaseQueryCompiler, QueryAdapter

__all__ = [
    # Types
    'FilterValue', 'FilterDict', 'OrderSpec', 'FieldsSpec',
    'FilterFormat', 'LogicalOperator', 'ComparisonOperator',
    'FilterInput', 'ASTNode', 'FieldCondition', 'LogicalCondition',
    'OrderNode', 'FieldsNode', 'FilterAST', 'BackendQuery',
    'QueryCompiler', 'ValidationRule', 'SecurityPolicy',
    
    # Errors
    'QEngineError', 'ParseError', 'ValidationError', 'SecurityError',
    'CompilerError', 'UnsupportedOperatorError', 'RegistryError',
    'OptimizationError',
    
    # Config
    'ParserConfig', 'ValidatorConfig', 'OptimizerConfig', 'CacheConfig',
    'QEngineConfig', 'default_config',
    
    # Components
    'FilterParser', 'FilterNormalizer', 'FilterValidator',
    'ASTBuilder', 'ASTOptimizer',
    'BaseQueryCompiler', 'QueryAdapter',
    
    # Registries
    'compiler_registry', 'operator_registry',
]
