---
title: 'core.registry'
description: 'Registry for managing query compilers and operators.'
navigation:
    title: 'core.registry'
    icon: 'i-codicon-library'
---

Registry for managing query compilers and operators.

## CompilerRegistry
::reference-header
---
description: >
    Registry for managing query compilers.
lang: 'python'
type: 'class'
navigation:
    title: 'CompilerRegistry'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class CompilerRegistry()
```

Registry for managing query compilers.

### register_compiler
::reference-header
---
description: >
    Register a query compiler for a backend.
lang: 'python'
type: 'method'
navigation:
    title: 'register_compiler'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def register_compiler(backend_name: str,
                      compiler_class: Type[QueryCompiler]) -> None
```

Register a query compiler for a backend.

**Arguments**:

- `backend_name` - Name of the backend (e.g., &#x27;beanie&#x27;, &#x27;sqlalchemy&#x27;)
- `compiler_class` - Class that implements QueryCompiler

### get_compiler
::reference-header
---
description: >
    Get a compiler instance for a backend.
lang: 'python'
type: 'method'
navigation:
    title: 'get_compiler'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def get_compiler(backend_name: str) -> QueryCompiler
```

Get a compiler instance for a backend.

**Arguments**:

- `backend_name` - Name of the backend
  

**Returns**:

  QueryCompiler instance
  

**Raises**:

- `RegistryError` - If backend is not registered

### is_registered
::reference-header
---
description: >
    Check if a backend is registered.
lang: 'python'
type: 'method'
navigation:
    title: 'is_registered'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def is_registered(backend_name: str) -> bool
```

Check if a backend is registered.

### list_backends
::reference-header
---
description: >
    List all registered backend names.
lang: 'python'
type: 'method'
navigation:
    title: 'list_backends'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def list_backends() -> List[str]
```

List all registered backend names.

### unregister_compiler
::reference-header
---
description: >
    Unregister a compiler.
lang: 'python'
type: 'method'
navigation:
    title: 'unregister_compiler'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def unregister_compiler(backend_name: str) -> None
```

Unregister a compiler.

## OperatorRegistry
::reference-header
---
description: >
    Registry for managing custom operators.
lang: 'python'
type: 'class'
navigation:
    title: 'OperatorRegistry'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class OperatorRegistry()
```

Registry for managing custom operators.

### register_operator
::reference-header
---
description: >
    Register a custom operator.
lang: 'python'
type: 'method'
navigation:
    title: 'register_operator'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def register_operator(name: str,
                      implementation: Any,
                      backends: Optional[List[str]] = None) -> None
```

Register a custom operator.

**Arguments**:

- `name` - Operator name (e.g., &#x27;$custom_op&#x27;)
- `implementation` - Operator implementation
- `backends` - List of backends this operator supports (None = all)

### get_operator
::reference-header
---
description: >
    Get operator implementation.
lang: 'python'
type: 'method'
navigation:
    title: 'get_operator'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def get_operator(name: str, backend: Optional[str] = None) -> Any
```

Get operator implementation.

**Arguments**:

- `name` - Operator name
- `backend` - Backend name (for backend-specific operators)
  

**Returns**:

  Operator implementation

### is_registered
::reference-header
---
description: >
    Check if an operator is registered.
lang: 'python'
type: 'method'
navigation:
    title: 'is_registered'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def is_registered(name: str, backend: Optional[str] = None) -> bool
```

Check if an operator is registered.

### list_operators
::reference-header
---
description: >
    List all registered operators.
lang: 'python'
type: 'method'
navigation:
    title: 'list_operators'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def list_operators(backend: Optional[str] = None) -> List[str]
```

List all registered operators.

