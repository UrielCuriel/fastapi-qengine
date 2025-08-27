"""
Registry for managing query compilers and operators.
"""
from typing import Dict, Type, Optional, List, Any
from abc import ABC, abstractmethod

from .types import QueryCompiler, FilterAST
from .errors import RegistryError


class CompilerRegistry:
    """Registry for managing query compilers."""
    
    def __init__(self):
        self._compilers: Dict[str, Type[QueryCompiler]] = {}
        self._instances: Dict[str, QueryCompiler] = {}
    
    def register_compiler(self, backend_name: str, compiler_class: Type[QueryCompiler]) -> None:
        """
        Register a query compiler for a backend.
        
        Args:
            backend_name: Name of the backend (e.g., 'beanie', 'sqlalchemy')
            compiler_class: Class that implements QueryCompiler
        """
        if not issubclass(compiler_class, QueryCompiler):
            raise RegistryError(f"Compiler class must implement QueryCompiler interface")
        
        self._compilers[backend_name] = compiler_class
        # Clear cached instance if exists
        if backend_name in self._instances:
            del self._instances[backend_name]
    
    def get_compiler(self, backend_name: str) -> QueryCompiler:
        """
        Get a compiler instance for a backend.
        
        Args:
            backend_name: Name of the backend
            
        Returns:
            QueryCompiler instance
            
        Raises:
            RegistryError: If backend is not registered
        """
        if backend_name not in self._compilers:
            raise RegistryError(f"No compiler registered for backend '{backend_name}'")
        
        # Use cached instance if available
        if backend_name not in self._instances:
            compiler_class = self._compilers[backend_name]
            self._instances[backend_name] = compiler_class()
        
        return self._instances[backend_name]
    
    def is_registered(self, backend_name: str) -> bool:
        """Check if a backend is registered."""
        return backend_name in self._compilers
    
    def list_backends(self) -> List[str]:
        """List all registered backend names."""
        return list(self._compilers.keys())
    
    def unregister_compiler(self, backend_name: str) -> None:
        """Unregister a compiler."""
        if backend_name in self._compilers:
            del self._compilers[backend_name]
        if backend_name in self._instances:
            del self._instances[backend_name]


class OperatorRegistry:
    """Registry for managing custom operators."""
    
    def __init__(self):
        self._operators: Dict[str, Dict[str, Any]] = {}
    
    def register_operator(self, name: str, implementation: Any, 
                         backends: Optional[List[str]] = None) -> None:
        """
        Register a custom operator.
        
        Args:
            name: Operator name (e.g., '$custom_op')
            implementation: Operator implementation
            backends: List of backends this operator supports (None = all)
        """
        if not name.startswith('$'):
            raise RegistryError("Operator names must start with '$'")
        
        self._operators[name] = {
            'implementation': implementation,
            'backends': backends or []
        }
    
    def get_operator(self, name: str, backend: Optional[str] = None) -> Any:
        """
        Get operator implementation.
        
        Args:
            name: Operator name
            backend: Backend name (for backend-specific operators)
            
        Returns:
            Operator implementation
        """
        if name not in self._operators:
            raise RegistryError(f"Unknown operator '{name}'")
        
        operator_info = self._operators[name]
        
        # Check backend compatibility
        if backend and operator_info['backends'] and backend not in operator_info['backends']:
            raise RegistryError(f"Operator '{name}' not supported for backend '{backend}'")
        
        return operator_info['implementation']
    
    def is_registered(self, name: str, backend: Optional[str] = None) -> bool:
        """Check if an operator is registered."""
        if name not in self._operators:
            return False
        
        if backend:
            operator_info = self._operators[name]
            return not operator_info['backends'] or backend in operator_info['backends']
        
        return True
    
    def list_operators(self, backend: Optional[str] = None) -> List[str]:
        """List all registered operators."""
        if backend:
            return [name for name, info in self._operators.items() 
                   if not info['backends'] or backend in info['backends']]
        return list(self._operators.keys())


# Global registries
compiler_registry = CompilerRegistry()
operator_registry = OperatorRegistry()
