---
title: 'core.normalizer'
description: 'Normalizer for filter inputs to canonical format.'
navigation:
    title: 'core.normalizer'
    icon: 'i-codicon-library'
---

Normalizer for filter inputs to canonical format.

## FilterNormalizer
::reference-header
---
description: >
    Normalizes filter inputs to a canonical format.
lang: 'python'
type: 'class'
navigation:
    title: 'FilterNormalizer'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class FilterNormalizer()
```

Normalizes filter inputs to a canonical format.

### normalize
::reference-header
---
description: >
    Normalize a FilterInput to canonical format.
lang: 'python'
type: 'method'
navigation:
    title: 'normalize'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def normalize(filter_input: FilterInput) -> FilterInput
```

Normalize a FilterInput to canonical format.

**Arguments**:

- `filter_input` - Raw FilterInput from parser
  

**Returns**:

  Normalized FilterInput with canonical structure

### _normalize_where
::reference-header
---
description: >
    Normalize where conditions to canonical format.
lang: 'python'
type: 'method'
navigation:
    title: '_normalize_where'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _normalize_where(where: FilterDict) -> FilterDict
```

Normalize where conditions to canonical format.

### _normalize_condition
::reference-header
---
description: >
    Recursively normalize a condition.
lang: 'python'
type: 'method'
navigation:
    title: '_normalize_condition'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _normalize_condition(condition: Any) -> Any
```

Recursively normalize a condition.

### _normalize_operator_value
::reference-header
---
description: >
    Normalize operator value.
lang: 'python'
type: 'method'
navigation:
    title: '_normalize_operator_value'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _normalize_operator_value(operator: str, value: Any) -> Any
```

Normalize operator value.

### _normalize_field_condition
::reference-header
---
description: >
    Normalize a field condition.
lang: 'python'
type: 'method'
navigation:
    title: '_normalize_field_condition'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _normalize_field_condition(condition: Any) -> Any
```

Normalize a field condition.

### _normalize_order
::reference-header
---
description: >
    Normalize order specification.
lang: 'python'
type: 'method'
navigation:
    title: '_normalize_order'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _normalize_order(order: OrderSpec) -> str
```

Normalize order specification.

### _normalize_fields
::reference-header
---
description: >
    Normalize fields specification.
lang: 'python'
type: 'method'
navigation:
    title: '_normalize_fields'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _normalize_fields(fields: FieldsSpec) -> Dict[str, int]
```

Normalize fields specification.

### _simplify_logical_operators
::reference-header
---
description: >
    Simplify redundant logical operators.
lang: 'python'
type: 'method'
navigation:
    title: '_simplify_logical_operators'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _simplify_logical_operators(condition: Dict[str, Any]) -> Dict[str, Any]
```

Simplify redundant logical operators.

### _process_logical_operator
::reference-header
---
description: >
    Process logical operators ($and, $or) and simplify them.
lang: 'python'
type: 'method'
navigation:
    title: '_process_logical_operator'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _process_logical_operator(operator: str, value: Any) -> Dict[str, Any]
```

Process logical operators ($and, $or) and simplify them.

### _handle_simplified_logical_items
::reference-header
---
description: >
    Handle simplified logical operator items.
lang: 'python'
type: 'method'
navigation:
    title: '_handle_simplified_logical_items'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _handle_simplified_logical_items(operator: str,
                                     items: list) -> Dict[str, Any]
```

Handle simplified logical operator items.

### _merge_single_logical_item
::reference-header
---
description: >
    Merge single logical operator item into parent.
lang: 'python'
type: 'method'
navigation:
    title: '_merge_single_logical_item'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _merge_single_logical_item(item: Any) -> Dict[str, Any]
```

Merge single logical operator item into parent.

### _process_regular_field
::reference-header
---
description: >
    Process regular field values.
lang: 'python'
type: 'method'
navigation:
    title: '_process_regular_field'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _process_regular_field(value: Any) -> Any
```

Process regular field values.

