---
title: 'operators.custom'
description: 'Custom operators and operator utilities.'
navigation:
    title: 'operators.custom'
    icon: 'i-codicon-library'
---

Custom operators and operator utilities.

## CustomOperatorHandler
::reference-header
---
description: >
    Base class for custom operator handlers.
lang: 'python'
type: 'class'
navigation:
    title: 'CustomOperatorHandler'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class CustomOperatorHandler(ABC)
```

Base class for custom operator handlers.

### compile
::reference-header
---
description: >
    Compile custom operator.
lang: 'python'
type: 'method'
navigation:
    title: 'compile'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
@abstractmethod
def compile(field: str, value: Any, backend: str) -> Any
```

Compile custom operator.

### supported_backends
::reference-header
---
description: >
    List of supported backends.
lang: 'python'
type: 'method'
navigation:
    title: 'supported_backends'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
@property
@abstractmethod
def supported_backends() -> list
```

List of supported backends.

## register_custom_operator
::reference-header
---
description: >
    Register a custom operator.
lang: 'python'
type: 'function'
navigation:
    title: 'register_custom_operator'
    icon: 'i-codicon-symbol-method'
    level: 1
---
::

```python
def register_custom_operator(name: str,
                             handler: CustomOperatorHandler) -> None
```

Register a custom operator.

**Arguments**:

- `name` - Operator name (must start with $)
- `handler` - Operator handler instance

## create_simple_operator
::reference-header
---
description: >
    Create and register a simple custom operator.
lang: 'python'
type: 'function'
navigation:
    title: 'create_simple_operator'
    icon: 'i-codicon-symbol-method'
    level: 1
---
::

```python
def create_simple_operator(name: str,
                           mongo_impl: Callable[[str, Any], Dict],
                           backends: list | None = None) -> None
```

Create and register a simple custom operator.

**Arguments**:

- `name` - Operator name
- `mongo_impl` - Function that takes (field, value) and returns MongoDB query dict
- `backends` - Supported backends (defaults to [&#x27;beanie&#x27;, &#x27;pymongo&#x27;])

## register_builtin_custom_operators
::reference-header
---
description: >
    Register built-in custom operators.
lang: 'python'
type: 'function'
navigation:
    title: 'register_builtin_custom_operators'
    icon: 'i-codicon-symbol-method'
    level: 1
---
::

```python
def register_builtin_custom_operators()
```

Register built-in custom operators.

## get_operator_handler
::reference-header
---
description: >
    Get handler for an operator.
lang: 'python'
type: 'function'
navigation:
    title: 'get_operator_handler'
    icon: 'i-codicon-symbol-method'
    level: 1
---
::

```python
def get_operator_handler(operator_name: str,
                         backend: str | None = None) -> Any
```

Get handler for an operator.

## compile_operator
::reference-header
---
description: >
    Compile an operator to backend-specific format.
lang: 'python'
type: 'function'
navigation:
    title: 'compile_operator'
    icon: 'i-codicon-symbol-method'
    level: 1
---
::

```python
def compile_operator(operator_name: str, field: str, value: Any,
                     backend: str) -> Any
```

Compile an operator to backend-specific format.

