"""
FastAPI dependency for query engine.
"""

from typing import Any, Dict, Optional, Type, Union

from fastapi import Depends, HTTPException, Query, Request

from .backends.beanie import BeanieQueryCompiler
from .core.ast import ASTBuilder
from .core.config import QEngineConfig, default_config
from .core.errors import QEngineError
from .core.normalizer import FilterNormalizer
from .core.optimizer import ASTOptimizer
from .core.parser import FilterParser
from .core.registry import compiler_registry
from .core.types import FilterAST, SecurityPolicy
from .core.validator import FilterValidator


class QueryEngine:
    """
    Main QueryEngine dependency for FastAPI.

    This class serves as the main entry point and Facade for the entire
    query processing pipeline.
    """

    def __init__(
        self,
        model_class: Optional[Type] = None,
        backend: str = "beanie",
        config: Optional[QEngineConfig] = None,
        security_policy: Optional[SecurityPolicy] = None,
    ):
        """
        Initialize QueryEngine.

        Args:
            model_class: Model class for the backend (e.g., Beanie Document)
            backend: Backend name ('beanie', 'pymongo', etc.)
            config: Custom configuration
            security_policy: Custom security policy
        """
        self.model_class = model_class
        self.backend = backend
        self.config = config or default_config
        self.security_policy = security_policy or self.config.security_policy

        # Initialize pipeline components
        self.parser = FilterParser(self.config.parser)
        self.normalizer = FilterNormalizer()
        self.validator = FilterValidator(self.config.validator, self.security_policy)
        self.ast_builder = ASTBuilder()
        self.optimizer = ASTOptimizer(self.config.optimizer)

        # Ensure backend compiler is registered
        if not compiler_registry.is_registered(backend):
            if backend == "beanie":
                compiler_registry.register_compiler("beanie", BeanieQueryCompiler)
            else:
                raise ValueError(f"Backend '{backend}' is not supported")

    def __call__(
        self,
        request: Request,
        filter: Optional[str] = Query(None, description="Filter specification (JSON string or nested params)"),
    ) -> Union[Dict[str, Any], FilterAST]:
        """
        FastAPI dependency that processes filter parameter.

        Args:
            request: FastAPI Request object to access all query parameters
            filter: Filter parameter from request

        Returns:
            Compiled query for the backend or FilterAST
        """
        try:
            # Get all query parameters
            query_params = dict(request.query_params)

            # Combine filter parameter with other query parameters for nested format
            if filter is None:
                # Check if we have nested filter params
                filter_params = {k: v for k, v in query_params.items() if k.startswith("filter[")}
                if filter_params:
                    filter_input = filter_params
                else:
                    # No filter specified
                    return self._get_empty_result()
            else:
                filter_input = filter

            # Process through pipeline
            ast = self.process_filter(filter_input)

            # Compile to backend format
            return self.compile_ast(ast)

        except QEngineError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            if self.config.debug:
                raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
            else:
                raise HTTPException(status_code=400, detail="Invalid filter specification")

    def process_filter(self, filter_input: Union[str, Dict[str, Any]]) -> FilterAST:
        """
        Process filter input through the complete pipeline.

        Args:
            filter_input: Raw filter input

        Returns:
            Optimized FilterAST
        """
        # 1. Parse
        parsed_input = self.parser.parse(filter_input)

        # 2. Normalize
        normalized_input = self.normalizer.normalize(parsed_input)

        # 3. Validate
        self.validator.validate_filter_input(normalized_input)

        # 4. Build AST
        ast = self.ast_builder.build(normalized_input)

        # 5. Optimize
        optimized_ast = self.optimizer.optimize(ast)

        return optimized_ast

    def compile_ast(self, ast: FilterAST) -> Any:
        """
        Compile AST to backend-specific query.

        Args:
            ast: FilterAST to compile

        Returns:
            Backend-specific query object
        """
        if self.backend == "beanie" and self.model_class:
            # Use BeanieQueryEngine for proper Beanie integration
            from .backends.beanie import BeanieQueryEngine

            engine = BeanieQueryEngine(self.model_class)
            return engine.build_query(ast)
        else:
            # Use registered compiler for other backends
            compiler = compiler_registry.get_compiler(self.backend)
            return compiler.compile(ast)

    def _get_empty_result(self) -> Any:
        """Get result for empty/no filter."""
        if self.backend == "beanie" and self.model_class:
            # Return tuple format for Beanie with empty query
            query = self.model_class.find()
            return (query, None, None)
        else:
            return {}  # Empty query for other backends

    # Convenience methods for different use cases

    def create_dependency(self):
        """Create a FastAPI dependency function."""
        return Depends(self)

    def parse_only(self, filter_input: Union[str, Dict[str, Any]]) -> FilterAST:
        """Parse filter input to AST without compilation."""
        return self.process_filter(filter_input)

    def compile_dict(self, filter_dict: Dict[str, Any]) -> Any:
        """Compile a filter dictionary directly."""
        ast = self.process_filter(filter_dict)
        return self.compile_ast(ast)


# Convenience factory functions


def create_beanie_dependency(
    model_class: Type, config: Optional[QEngineConfig] = None, security_policy: Optional[SecurityPolicy] = None
) -> QueryEngine:
    """
    Create a QueryEngine dependency for Beanie models.

    Args:
        model_class: Beanie Document class
        config: Custom configuration
        security_policy: Custom security policy

    Returns:
        QueryEngine instance configured for Beanie
    """
    return QueryEngine(model_class=model_class, backend="beanie", config=config, security_policy=security_policy)


def create_pymongo_dependency(
    config: Optional[QEngineConfig] = None,
    security_policy: Optional[SecurityPolicy] = None,
) -> QueryEngine:
    """
    Create a QueryEngine dependency for PyMongo.

    Args:
        collection_name: MongoDB collection name
        config: Custom configuration
        security_policy: Custom security policy

    Returns:
        QueryEngine instance configured for PyMongo
    """
    return QueryEngine(backend="pymongo", config=config, security_policy=security_policy)


# Global instances for common use cases
default_engine = QueryEngine()
beanie_engine = QueryEngine(backend="beanie")
