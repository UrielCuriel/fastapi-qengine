---
title: 'openapi_schema'
description: 'OpenAPI schema generation for query filters.'
navigation:
    title: 'openapi_schema'
    icon: 'i-codicon-library'
---

OpenAPI schema generation for query filters.

## FilterSchemaGenerator
::reference-header
---
description: >
    Generates OpenAPI schemas for filter parameters based on model classes.
lang: 'python'
type: 'class'
navigation:
    title: 'FilterSchemaGenerator'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class FilterSchemaGenerator()
```

Generates OpenAPI schemas for filter parameters based on model classes.

### _get_model_fields
::reference-header
---
description: >
    Extract field information from model.
lang: 'python'
type: 'method'
navigation:
    title: '_get_model_fields'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _get_model_fields() -> Dict[str, Dict[str, Any]]
```

Extract field information from model.

### _extract_pydantic_v2_fields
::reference-header
---
description: >
    Extract fields from Pydantic v2 model.
lang: 'python'
type: 'method'
navigation:
    title: '_extract_pydantic_v2_fields'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _extract_pydantic_v2_fields() -> Dict[str, Dict[str, Any]]
```

Extract fields from Pydantic v2 model.

### _extract_pydantic_v1_fields
::reference-header
---
description: >
    Extract fields from Pydantic v1 model.
lang: 'python'
type: 'method'
navigation:
    title: '_extract_pydantic_v1_fields'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _extract_pydantic_v1_fields() -> Dict[str, Dict[str, Any]]
```

Extract fields from Pydantic v1 model.

### _extract_fallback_fields
::reference-header
---
description: >
    Extract fields using type hints or basic fallback.
lang: 'python'
type: 'method'
navigation:
    title: '_extract_fallback_fields'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _extract_fallback_fields() -> Dict[str, Dict[str, Any]]
```

Extract fields using type hints or basic fallback.

### _get_basic_fallback_fields
::reference-header
---
description: >
    Return basic fallback fields when all else fails.
lang: 'python'
type: 'method'
navigation:
    title: '_get_basic_fallback_fields'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _get_basic_fallback_fields() -> Dict[str, Dict[str, Any]]
```

Return basic fallback fields when all else fails.

### _get_openapi_type
::reference-header
---
description: >
    Convert Python type to OpenAPI type.
lang: 'python'
type: 'method'
navigation:
    title: '_get_openapi_type'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _get_openapi_type(python_type: Type) -> Dict[str, Any]
```

Convert Python type to OpenAPI type.

### generate_field_schema
::reference-header
---
description: >
    Generate schema for a field.
lang: 'python'
type: 'method'
navigation:
    title: 'generate_field_schema'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def generate_field_schema(field_name: str,
                          field_info: Dict[str, Any]) -> Dict[str, Any]
```

Generate schema for a field.

### generate_filter_schema
::reference-header
---
description: >
    Generate complete filter schema.
lang: 'python'
type: 'method'
navigation:
    title: 'generate_filter_schema'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def generate_filter_schema() -> Dict[str, Any]
```

Generate complete filter schema.

### generate_examples
::reference-header
---
description: >
    Generate example queries.
lang: 'python'
type: 'method'
navigation:
    title: 'generate_examples'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def generate_examples() -> Dict[str, Any]
```

Generate example queries.

## generate_filter_docs
::reference-header
---
description: >
    Generate comprehensive OpenAPI documentation for filters.
lang: 'python'
type: 'function'
navigation:
    title: 'generate_filter_docs'
    icon: 'i-codicon-symbol-method'
    level: 1
---
::

```python
def generate_filter_docs(model_class: Type) -> Dict[str, Any]
```

Generate comprehensive OpenAPI documentation for filters.

**Arguments**:

- `model_class` - Model class to document
  

**Returns**:

  Dictionary with schemas and examples for OpenAPI spec

## add_filter_docs_to_endpoint
::reference-header
---
description: >
    Decorator to add filter documentation to FastAPI endpoint.
lang: 'python'
type: 'function'
navigation:
    title: 'add_filter_docs_to_endpoint'
    icon: 'i-codicon-symbol-method'
    level: 1
---
::

```python
def add_filter_docs_to_endpoint(model_class: Type)
```

Decorator to add filter documentation to FastAPI endpoint.

Usage:
    @app.get(&quot;/products&quot;)
    @add_filter_docs_to_endpoint(Product)
    def get_products(filter_query: dict = Depends(query_engine)):
        ...

