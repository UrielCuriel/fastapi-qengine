---
title: 'core.compiler_base'
description: 'Base compiler class and interfaces.'
navigation:
    title: 'core.compiler_base'
    icon: 'i-codicon-library'
---

Base compiler class and interfaces.

## BaseQueryCompiler
::reference-header
---
description: >
    Base class for all query compilers implementing Template Method pattern.
lang: 'python'
type: 'class'
navigation:
    title: 'BaseQueryCompiler'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class BaseQueryCompiler(QueryCompiler)
```

Base class for all query compilers implementing Template Method pattern.

### compile
::reference-header
---
description: >
    Template method for compiling FilterAST to backend query.
lang: 'python'
type: 'method'
navigation:
    title: 'compile'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def compile(ast: FilterAST) -> Any
```

Template method for compiling FilterAST to backend query.

**Arguments**:

- `ast` - FilterAST to compile
  

**Returns**:

  Backend-specific query object

### create_base_query
::reference-header
---
description: >
    Create the base query object for this backend.
lang: 'python'
type: 'method'
navigation:
    title: 'create_base_query'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
@abstractmethod
def create_base_query() -> Any
```

Create the base query object for this backend.

### apply_where
::reference-header
---
description: >
    Apply where conditions to the query.
lang: 'python'
type: 'method'
navigation:
    title: 'apply_where'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
@abstractmethod
def apply_where(query: Any, where_node: ASTNode) -> Any
```

Apply where conditions to the query.

### apply_order
::reference-header
---
description: >
    Apply ordering to the query.
lang: 'python'
type: 'method'
navigation:
    title: 'apply_order'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
@abstractmethod
def apply_order(query: Any, order_nodes: List[OrderNode]) -> Any
```

Apply ordering to the query.

### apply_fields
::reference-header
---
description: >
    Apply field projection to the query.
lang: 'python'
type: 'method'
navigation:
    title: 'apply_fields'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
@abstractmethod
def apply_fields(query: Any, fields_node: FieldsNode) -> Any
```

Apply field projection to the query.

### finalize_query
::reference-header
---
description: >
    Finalize the query before returning (default: return as-is).
lang: 'python'
type: 'method'
navigation:
    title: 'finalize_query'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def finalize_query(query: Any) -> Any
```

Finalize the query before returning (default: return as-is).

### supports_backend
::reference-header
---
description: >
    Check if this compiler supports the given backend.
lang: 'python'
type: 'method'
navigation:
    title: 'supports_backend'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def supports_backend(backend_type: str) -> bool
```

Check if this compiler supports the given backend.

### compile_condition
::reference-header
---
description: >
    Compile a condition node to backend-specific format.
lang: 'python'
type: 'method'
navigation:
    title: 'compile_condition'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def compile_condition(condition: ASTNode) -> Any
```

Compile a condition node to backend-specific format.

### compile_field_condition
::reference-header
---
description: >
    Compile a field condition to backend-specific format.
lang: 'python'
type: 'method'
navigation:
    title: 'compile_field_condition'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
@abstractmethod
def compile_field_condition(condition: FieldCondition) -> Any
```

Compile a field condition to backend-specific format.

### compile_logical_condition
::reference-header
---
description: >
    Compile a logical condition to backend-specific format.
lang: 'python'
type: 'method'
navigation:
    title: 'compile_logical_condition'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
@abstractmethod
def compile_logical_condition(condition: LogicalCondition) -> Any
```

Compile a logical condition to backend-specific format.

## QueryAdapter
::reference-header
---
description: >
    Adapter interface for different query object types.
lang: 'python'
type: 'class'
navigation:
    title: 'QueryAdapter'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class QueryAdapter(ABC)
```

Adapter interface for different query object types.

### add_where_condition
::reference-header
---
description: >
    Add a where condition to the query.
lang: 'python'
type: 'method'
navigation:
    title: 'add_where_condition'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
@abstractmethod
def add_where_condition(condition: Any) -> "QueryAdapter"
```

Add a where condition to the query.

### add_sort
::reference-header
---
description: >
    Add sorting to the query.
lang: 'python'
type: 'method'
navigation:
    title: 'add_sort'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
@abstractmethod
def add_sort(field: str, ascending: bool = True) -> "QueryAdapter"
```

Add sorting to the query.

### set_projection
::reference-header
---
description: >
    Set field projection.
lang: 'python'
type: 'method'
navigation:
    title: 'set_projection'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
@abstractmethod
def set_projection(fields: Dict[str, int]) -> "QueryAdapter"
```

Set field projection.

### build
::reference-header
---
description: >
    Build the final query object.
lang: 'python'
type: 'method'
navigation:
    title: 'build'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
@abstractmethod
def build() -> Any
```

Build the final query object.

