---
title: 'backends.beanie'
description: 'Beanie/PyMongo backend compiler.'
navigation:
    title: 'backends.beanie'
    icon: 'i-codicon-library'
---

Beanie/PyMongo backend compiler.

## BeanieQueryAdapter
::reference-header
---
description: >
    Adapter for Beanie/PyMongo query objects.
lang: 'python'
type: 'class'
navigation:
    title: 'BeanieQueryAdapter'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class BeanieQueryAdapter(QueryAdapter)
```

Adapter for Beanie/PyMongo query objects.

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
def add_where_condition(condition: Dict[str, Any]) -> "BeanieQueryAdapter"
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
def add_sort(field: str, ascending: bool = True) -> "BeanieQueryAdapter"
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
def set_projection(fields: Dict[str, int]) -> "BeanieQueryAdapter"
```

Set field projection.

### build
::reference-header
---
description: >
    Build the final query components.
lang: 'python'
type: 'method'
navigation:
    title: 'build'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def build() -> Dict[str, Any]
```

Build the final query components.

## BeanieQueryCompiler
::reference-header
---
description: >
    Query compiler for Beanie/PyMongo backend.
lang: 'python'
type: 'class'
navigation:
    title: 'BeanieQueryCompiler'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class BeanieQueryCompiler(BaseQueryCompiler)
```

Query compiler for Beanie/PyMongo backend.

### create_base_query
::reference-header
---
description: >
    Create the base query adapter for Beanie.
lang: 'python'
type: 'method'
navigation:
    title: 'create_base_query'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def create_base_query() -> BeanieQueryAdapter
```

Create the base query adapter for Beanie.

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
def apply_where(query: BeanieQueryAdapter,
                where_node: ASTNode) -> BeanieQueryAdapter
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
def apply_order(query: BeanieQueryAdapter,
                order_nodes: List[OrderNode]) -> BeanieQueryAdapter
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
def apply_fields(query: BeanieQueryAdapter,
                 fields_node: FieldsNode) -> BeanieQueryAdapter
```

Apply field projection to the query.

### finalize_query
::reference-header
---
description: >
    Finalize the query and return MongoDB query components.
lang: 'python'
type: 'method'
navigation:
    title: 'finalize_query'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def finalize_query(query: BeanieQueryAdapter) -> Dict[str, Any]
```

Finalize the query and return MongoDB query components.

### compile_field_condition
::reference-header
---
description: >
    Compile a field condition to MongoDB format.
lang: 'python'
type: 'method'
navigation:
    title: 'compile_field_condition'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def compile_field_condition(condition: FieldCondition) -> Dict[str, Any]
```

Compile a field condition to MongoDB format.

### compile_logical_condition
::reference-header
---
description: >
    Compile a logical condition to MongoDB format.
lang: 'python'
type: 'method'
navigation:
    title: 'compile_logical_condition'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def compile_logical_condition(condition: LogicalCondition) -> Dict[str, Any]
```

Compile a logical condition to MongoDB format.

## BeanieQueryEngine
::reference-header
---
description: >
    High-level query engine for Beanie models.
lang: 'python'
type: 'class'
navigation:
    title: 'BeanieQueryEngine'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class BeanieQueryEngine()
```

High-level query engine for Beanie models.

### __init__
::reference-header
---
description: >
    Initialize query engine for a Beanie model.
lang: 'python'
type: 'method'
navigation:
    title: '__init__'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def __init__(model_class)
```

Initialize query engine for a Beanie model.

**Arguments**:

- `model_class` - Beanie Document class

### build_query
::reference-header
---
description: >
    Build a Beanie query from FilterAST.
lang: 'python'
type: 'method'
navigation:
    title: 'build_query'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def build_query(ast: FilterAST)
```

Build a Beanie query from FilterAST.

**Arguments**:

- `ast` - FilterAST to compile
  

**Returns**:

  Beanie query object

### execute_query
::reference-header
---
description: >
    Execute query and return results.
lang: 'python'
type: 'method'
navigation:
    title: 'execute_query'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def execute_query(ast: FilterAST)
```

Execute query and return results.

**Arguments**:

- `ast` - FilterAST to execute
  

**Returns**:

  Query results

## compile_to_mongodb
::reference-header
---
description: >
    Compile FilterAST directly to MongoDB query components.
lang: 'python'
type: 'function'
navigation:
    title: 'compile_to_mongodb'
    icon: 'i-codicon-symbol-method'
    level: 1
---
::

```python
def compile_to_mongodb(ast: FilterAST) -> Dict[str, Any]
```

Compile FilterAST directly to MongoDB query components.

**Arguments**:

- `ast` - FilterAST to compile
  

**Returns**:

  Dict with &#x27;filter&#x27;, &#x27;sort&#x27;, and/or &#x27;projection&#x27; keys

