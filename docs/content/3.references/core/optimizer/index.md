---
title: 'core.optimizer'
description: 'AST Optimizer for simplifying and optimizing filter ASTs.'
navigation:
    title: 'core.optimizer'
    icon: 'i-codicon-library'
---

AST Optimizer for simplifying and optimizing filter ASTs.

## ASTOptimizer
::reference-header
---
description: >
    Optimizes filter ASTs for better performance.
lang: 'python'
type: 'class'
navigation:
    title: 'ASTOptimizer'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class ASTOptimizer()
```

Optimizes filter ASTs for better performance.

### optimize
::reference-header
---
description: >
    Optimize a FilterAST.
lang: 'python'
type: 'method'
navigation:
    title: 'optimize'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def optimize(ast: FilterAST) -> FilterAST
```

Optimize a FilterAST.

**Arguments**:

- `ast` - Input FilterAST
  

**Returns**:

  Optimized FilterAST

### _optimize_node
::reference-header
---
description: >
    Optimize a single AST node.
lang: 'python'
type: 'method'
navigation:
    title: '_optimize_node'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _optimize_node(node: ASTNode) -> ASTNode
```

Optimize a single AST node.

### _optimize_logical_condition
::reference-header
---
description: >
    Optimize a logical condition node.
lang: 'python'
type: 'method'
navigation:
    title: '_optimize_logical_condition'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _optimize_logical_condition(node: LogicalCondition) -> ASTNode | None
```

Optimize a logical condition node.

### _optimize_field_condition
::reference-header
---
description: >
    Optimize a field condition node.
lang: 'python'
type: 'method'
navigation:
    title: '_optimize_field_condition'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _optimize_field_condition(node: FieldCondition) -> FieldCondition
```

Optimize a field condition node.

### _simplify_logical_operators
::reference-header
---
description: >
    Simplify nested logical operators of the same type.
lang: 'python'
type: 'method'
navigation:
    title: '_simplify_logical_operators'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _simplify_logical_operators(operator: LogicalOperator,
                                conditions: List[ASTNode]) -> List[ASTNode]
```

Simplify nested logical operators of the same type.

### _combine_range_conditions
::reference-header
---
description: >
    Combine range conditions on the same field.
lang: 'python'
type: 'method'
navigation:
    title: '_combine_range_conditions'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _combine_range_conditions(conditions: List[ASTNode]) -> List[ASTNode]
```

Combine range conditions on the same field.

### _try_combine_field_conditions
::reference-header
---
description: >
    Try to combine multiple conditions on the same field.
lang: 'python'
type: 'method'
navigation:
    title: '_try_combine_field_conditions'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _try_combine_field_conditions(
        conditions: List[FieldCondition]) -> List[FieldCondition]
```

Try to combine multiple conditions on the same field.

### _remove_redundant_conditions
::reference-header
---
description: >
    Remove redundant conditions.
lang: 'python'
type: 'method'
navigation:
    title: '_remove_redundant_conditions'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _remove_redundant_conditions(conditions: List[ASTNode]) -> List[ASTNode]
```

Remove redundant conditions.

### _get_condition_key
::reference-header
---
description: >
    Get a string key for a condition for deduplication.
lang: 'python'
type: 'method'
navigation:
    title: '_get_condition_key'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _get_condition_key(condition: ASTNode) -> str
```

Get a string key for a condition for deduplication.

### _optimize_order_nodes
::reference-header
---
description: >
    Optimize order nodes.
lang: 'python'
type: 'method'
navigation:
    title: '_optimize_order_nodes'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _optimize_order_nodes(order_nodes: List[OrderNode]) -> List[OrderNode]
```

Optimize order nodes.

### _nodes_equal
::reference-header
---
description: >
    Check if two nodes are equal.
lang: 'python'
type: 'method'
navigation:
    title: '_nodes_equal'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _nodes_equal(node1: Optional[ASTNode], node2: Optional[ASTNode]) -> bool
```

Check if two nodes are equal.

### _field_conditions_equal
::reference-header
---
description: >
    Check if two field conditions are equal.
lang: 'python'
type: 'method'
navigation:
    title: '_field_conditions_equal'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _field_conditions_equal(node1: FieldCondition,
                            node2: FieldCondition) -> bool
```

Check if two field conditions are equal.

### _logical_conditions_equal
::reference-header
---
description: >
    Check if two logical conditions are equal.
lang: 'python'
type: 'method'
navigation:
    title: '_logical_conditions_equal'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _logical_conditions_equal(node1: LogicalCondition,
                              node2: LogicalCondition) -> bool
```

Check if two logical conditions are equal.

### _commutative_conditions_equal
::reference-header
---
description: >
    Check if two lists of conditions are equal for commutative operators.
lang: 'python'
type: 'method'
navigation:
    title: '_commutative_conditions_equal'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _commutative_conditions_equal(conditions1: List[ASTNode],
                                  conditions2: List[ASTNode]) -> bool
```

Check if two lists of conditions are equal for commutative operators.

### _ordered_conditions_equal
::reference-header
---
description: >
    Check if two lists of conditions are equal in order.
lang: 'python'
type: 'method'
navigation:
    title: '_ordered_conditions_equal'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def _ordered_conditions_equal(conditions1: List[ASTNode],
                              conditions2: List[ASTNode]) -> bool
```

Check if two lists of conditions are equal in order.

