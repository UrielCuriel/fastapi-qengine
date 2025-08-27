---
title: 'core.parser'
description: 'Parser for filter inputs in different formats.'
navigation:
    title: 'core.parser'
    icon: 'i-codicon-library'
---

Parser for filter inputs in different formats.

## FilterParser
::reference-header
---
description: >
    Parses filter inputs from various formats.
lang: 'python'
type: 'class'
navigation:
    title: 'FilterParser'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class FilterParser()
```

Parses filter inputs from various formats.

### parse
::reference-header
---
description: >
    Parse filter input and return a normalized FilterInput object.
lang: 'python'
type: 'method'
navigation:
    title: 'parse'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def parse(filter_input: Union[str, Dict[str, Any]]) -> FilterInput
```

Parse filter input and return a normalized FilterInput object.

**Arguments**:

- `filter_input` - Can be a JSON string, dict, or nested params dict
  

**Returns**:

  FilterInput object with normalized data

### _parse_json_string
::reference-header
---
description: >
    Parse a JSON string filter.
lang: 'python'
type: 'method'
navigation:
    title: '_parse_json_string'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _parse_json_string(json_str: str) -> FilterInput
```

Parse a JSON string filter.

### _parse_dict_input
::reference-header
---
description: >
    Parse a dictionary input (could be nested params or direct dict).
lang: 'python'
type: 'method'
navigation:
    title: '_parse_dict_input'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _parse_dict_input(data: Dict[str, Any]) -> FilterInput
```

Parse a dictionary input (could be nested params or direct dict).

### _is_nested_params_format
::reference-header
---
description: >
    Check if the data looks like nested params format.
lang: 'python'
type: 'method'
navigation:
    title: '_is_nested_params_format'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _is_nested_params_format(data: Dict[str, Any]) -> bool
```

Check if the data looks like nested params format.

### _parse_nested_params
::reference-header
---
description: >
    Parse nested parameters format like filter[where][field]=value.
lang: 'python'
type: 'method'
navigation:
    title: '_parse_nested_params'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _parse_nested_params(data: Dict[str, Any]) -> FilterInput
```

Parse nested parameters format like filter[where][field]=value.

### _parse_nested_key
::reference-header
---
description: >
    Parse a nested key like 'filter[where][price][$gt]' into parts.
lang: 'python'
type: 'method'
navigation:
    title: '_parse_nested_key'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _parse_nested_key(key: str) -> list
```

Parse a nested key like &#x27;filter[where][price][$gt]&#x27; into parts.

**Returns**:

  List of key parts like [&#x27;filter&#x27;, &#x27;where&#x27;, &#x27;price&#x27;, &#x27;$gt&#x27;]

### _convert_value
::reference-header
---
description: >
    Convert string values to appropriate types.
lang: 'python'
type: 'method'
navigation:
    title: '_convert_value'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _convert_value(value: Any) -> Any
```

Convert string values to appropriate types.

### validate_depth
::reference-header
---
description: >
    Validate nesting depth doesn't exceed configuration limits.
lang: 'python'
type: 'method'
navigation:
    title: 'validate_depth'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def validate_depth(data: Dict[str, Any], current_depth: int = 0) -> None
```

Validate nesting depth doesn&#x27;t exceed configuration limits.

