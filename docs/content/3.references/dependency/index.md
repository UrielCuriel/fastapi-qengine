---
title: 'dependency'
description: 'FastAPI dependency for query engine.'
navigation:
    title: 'dependency'
    icon: 'i-codicon-library'
---

FastAPI dependency for query engine.

## QueryEngine
::reference-header
---
description: >
    Main QueryEngine dependency for FastAPI.
lang: 'python'
type: 'class'
navigation:
    title: 'QueryEngine'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class QueryEngine()
```

Main QueryEngine dependency for FastAPI.

This class serves as the main entry point and Facade for the entire
query processing pipeline.

### __init__
::reference-header
---
description: >
    Initialize QueryEngine.
lang: 'python'
type: 'method'
navigation:
    title: '__init__'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def __init__(model_class: Optional[Type] = None,
             backend: str = "beanie",
             config: Optional[QEngineConfig] = None,
             security_policy: Optional[SecurityPolicy] = None)
```

Initialize QueryEngine.

**Arguments**:

- `model_class` - Model class for the backend (e.g., Beanie Document)
- `backend` - Backend name (&#x27;beanie&#x27;, &#x27;pymongo&#x27;, etc.)
- `config` - Custom configuration
- `security_policy` - Custom security policy

### __call__
::reference-header
---
description: >
    FastAPI dependency that processes filter parameter.
lang: 'python'
type: 'method'
navigation:
    title: '__call__'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def __call__(
    request: Request,
    filter: Optional[str] = Query(
        None,
        description="Filter specification (JSON string or nested params)")
) -> Union[Dict[str, Any], FilterAST]
```

FastAPI dependency that processes filter parameter.

**Arguments**:

- `request` - FastAPI Request object to access all query parameters
- `filter` - Filter parameter from request
  

**Returns**:

  Compiled query for the backend or FilterAST

### process_filter
::reference-header
---
description: >
    Process filter input through the complete pipeline.
lang: 'python'
type: 'method'
navigation:
    title: 'process_filter'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def process_filter(filter_input: Union[str, Dict[str, Any]]) -> FilterAST
```

Process filter input through the complete pipeline.

**Arguments**:

- `filter_input` - Raw filter input
  

**Returns**:

  Optimized FilterAST

### compile_ast
::reference-header
---
description: >
    Compile AST to backend-specific query.
lang: 'python'
type: 'method'
navigation:
    title: 'compile_ast'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def compile_ast(ast: FilterAST) -> Any
```

Compile AST to backend-specific query.

**Arguments**:

- `ast` - FilterAST to compile
  

**Returns**:

  Backend-specific query object

### _get_empty_result
::reference-header
---
description: >
    Get result for empty/no filter.
lang: 'python'
type: 'method'
navigation:
    title: '_get_empty_result'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _get_empty_result() -> Dict[str, Any]
```

Get result for empty/no filter.

### create_dependency
::reference-header
---
description: >
    Create a FastAPI dependency function.
lang: 'python'
type: 'method'
navigation:
    title: 'create_dependency'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def create_dependency()
```

Create a FastAPI dependency function.

### parse_only
::reference-header
---
description: >
    Parse filter input to AST without compilation.
lang: 'python'
type: 'method'
navigation:
    title: 'parse_only'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def parse_only(filter_input: Union[str, Dict[str, Any]]) -> FilterAST
```

Parse filter input to AST without compilation.

### compile_dict
::reference-header
---
description: >
    Compile a filter dictionary directly.
lang: 'python'
type: 'method'
navigation:
    title: 'compile_dict'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def compile_dict(filter_dict: Dict[str, Any]) -> Any
```

Compile a filter dictionary directly.

## create_beanie_dependency
::reference-header
---
description: >
    Create a QueryEngine dependency for Beanie models.
lang: 'python'
type: 'function'
navigation:
    title: 'create_beanie_dependency'
    icon: 'i-codicon-symbol-method'
    level: 1
---
::

```python
def create_beanie_dependency(
        model_class: Type,
        config: Optional[QEngineConfig] = None,
        security_policy: Optional[SecurityPolicy] = None) -> QueryEngine
```

Create a QueryEngine dependency for Beanie models.

**Arguments**:

- `model_class` - Beanie Document class
- `config` - Custom configuration
- `security_policy` - Custom security policy
  

**Returns**:

  QueryEngine instance configured for Beanie

## create_pymongo_dependency
::reference-header
---
description: >
    Create a QueryEngine dependency for PyMongo.
lang: 'python'
type: 'function'
navigation:
    title: 'create_pymongo_dependency'
    icon: 'i-codicon-symbol-method'
    level: 1
---
::

```python
def create_pymongo_dependency(
        config: Optional[QEngineConfig] = None,
        security_policy: Optional[SecurityPolicy] = None) -> QueryEngine
```

Create a QueryEngine dependency for PyMongo.

**Arguments**:

- `collection_name` - MongoDB collection name
- `config` - Custom configuration
- `security_policy` - Custom security policy
  

**Returns**:

  QueryEngine instance configured for PyMongo

