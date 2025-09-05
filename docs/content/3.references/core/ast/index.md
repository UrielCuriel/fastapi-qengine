---
title: 'core.ast'
description: 'AST Builder for converting normalized filter inputs to typed AST nodes.'
navigation:
    title: 'core.ast'
    icon: 'i-codicon-library'
---

AST Builder for converting normalized filter inputs to typed AST nodes.

## ASTBuilder
::reference-header
---
description: >
    Builds typed AST from normalized filter inputs.
lang: 'python'
type: 'class'
navigation:
    title: 'ASTBuilder'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class ASTBuilder()
```

Builds typed AST from normalized filter inputs.

### build
::reference-header
---
description: >
    Build a FilterAST from a normalized FilterInput.
lang: 'python'
type: 'method'
navigation:
    title: 'build'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def build(filter_input: FilterInput) -> FilterAST
```

Build a FilterAST from a normalized FilterInput.

**Arguments**:

- `filter_input` - Normalized FilterInput
  

**Returns**:

  FilterAST with typed nodes

### _build_where_node
::reference-header
---
description: >
    Build where clause AST node.
lang: 'python'
type: 'method'
navigation:
    title: '_build_where_node'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _build_where_node(where: Dict[str, Any]) -> ASTNode
```

Build where clause AST node.

### _build_condition_node
::reference-header
---
description: >
    Build a condition node (field condition or logical condition).
lang: 'python'
type: 'method'
navigation:
    title: '_build_condition_node'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _build_condition_node(condition: Dict[str, Any]) -> ASTNode
```

Build a condition node (field condition or logical condition).

### _build_field_condition
::reference-header
---
description: >
    Build a field condition node.
lang: 'python'
type: 'method'
navigation:
    title: '_build_field_condition'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _build_field_condition(field: str, condition: Any) -> ASTNode
```

Build a field condition node.

### _build_complex_field_condition
::reference-header
---
description: >
    Build a complex field condition with operators.
lang: 'python'
type: 'method'
navigation:
    title: '_build_complex_field_condition'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _build_complex_field_condition(field: str,
                                   condition: Dict[str, Any]) -> ASTNode
```

Build a complex field condition with operators.

### _build_single_operator_condition
::reference-header
---
description: >
    Build a field condition with a single operator.
lang: 'python'
type: 'method'
navigation:
    title: '_build_single_operator_condition'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _build_single_operator_condition(
        field: str, condition: Dict[str, Any]) -> FieldCondition
```

Build a field condition with a single operator.

### _build_multiple_operator_condition
::reference-header
---
description: >
    Build a field condition with multiple operators combined with AND.
lang: 'python'
type: 'method'
navigation:
    title: '_build_multiple_operator_condition'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _build_multiple_operator_condition(field: str,
                                       condition: Dict[str, Any]) -> ASTNode
```

Build a field condition with multiple operators combined with AND.

### _build_simple_field_condition
::reference-header
---
description: >
    Build a simple equality field condition.
lang: 'python'
type: 'method'
navigation:
    title: '_build_simple_field_condition'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _build_simple_field_condition(field: str,
                                  condition: Any) -> FieldCondition
```

Build a simple equality field condition.

### _validate_operator
::reference-header
---
description: >
    Validate that an operator key is valid.
lang: 'python'
type: 'method'
navigation:
    title: '_validate_operator'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _validate_operator(op_key: str) -> None
```

Validate that an operator key is valid.

### _get_comparison_operator
::reference-header
---
description: >
    Get a ComparisonOperator from an operator key.
lang: 'python'
type: 'method'
navigation:
    title: '_get_comparison_operator'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _get_comparison_operator(op_key: str) -> ComparisonOperator
```

Get a ComparisonOperator from an operator key.

### _build_order_nodes
::reference-header
---
description: >
    Build order nodes from order specification.
lang: 'python'
type: 'method'
navigation:
    title: '_build_order_nodes'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _build_order_nodes(order: str) -> List[OrderNode]
```

Build order nodes from order specification.

### _build_fields_node
::reference-header
---
description: >
    Build fields node from fields specification.
lang: 'python'
type: 'method'
navigation:
    title: '_build_fields_node'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _build_fields_node(fields: Dict[str, int]) -> FieldsNode
```

Build fields node from fields specification.

### _flatten_single_item_logical
::reference-header
---
description: >
    Flatten single-item logical conditions.
lang: 'python'
type: 'method'
navigation:
    title: '_flatten_single_item_logical'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _flatten_single_item_logical(node: ASTNode) -> ASTNode
```

Flatten single-item logical conditions.

