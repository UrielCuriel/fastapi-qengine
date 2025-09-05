---
title: 'core.types'
description: 'Type definitions for fastapi-qengine.'
navigation:
    title: 'core.types'
    icon: 'i-codicon-library'
---

Type definitions for fastapi-qengine.

## FilterFormat
::reference-header
---
description: >
    Supported filter input formats.
lang: 'python'
type: 'class'
navigation:
    title: 'FilterFormat'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class FilterFormat(Enum)
```

Supported filter input formats.

## LogicalOperator
::reference-header
---
description: >
    Logical operators for combining conditions.
lang: 'python'
type: 'class'
navigation:
    title: 'LogicalOperator'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class LogicalOperator(Enum)
```

Logical operators for combining conditions.

## ComparisonOperator
::reference-header
---
description: >
    Comparison operators for field conditions.
lang: 'python'
type: 'class'
navigation:
    title: 'ComparisonOperator'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class ComparisonOperator(Enum)
```

Comparison operators for field conditions.

### EQ
::reference-header
---
description: >
    Equal
lang: 'python'
type: 'variable'
navigation:
    title: 'EQ'
    icon: 'i-codicon-symbol-variable'
    level: 2
---

```python
EQ = "$eq"
```
::

Equal

### NE
::reference-header
---
description: >
    Not equal
lang: 'python'
type: 'variable'
navigation:
    title: 'NE'
    icon: 'i-codicon-symbol-variable'
    level: 2
---

```python
NE = "$ne"
```
::

Not equal

### GT
::reference-header
---
description: >
    Greater than
lang: 'python'
type: 'variable'
navigation:
    title: 'GT'
    icon: 'i-codicon-symbol-variable'
    level: 2
---

```python
GT = "$gt"
```
::

Greater than

### GTE
::reference-header
---
description: >
    Greater than or equal
lang: 'python'
type: 'variable'
navigation:
    title: 'GTE'
    icon: 'i-codicon-symbol-variable'
    level: 2
---

```python
GTE = "$gte"
```
::

Greater than or equal

### LT
::reference-header
---
description: >
    Less than
lang: 'python'
type: 'variable'
navigation:
    title: 'LT'
    icon: 'i-codicon-symbol-variable'
    level: 2
---

```python
LT = "$lt"
```
::

Less than

### LTE
::reference-header
---
description: >
    Less than or equal
lang: 'python'
type: 'variable'
navigation:
    title: 'LTE'
    icon: 'i-codicon-symbol-variable'
    level: 2
---

```python
LTE = "$lte"
```
::

Less than or equal

### IN
::reference-header
---
description: >
    In array
lang: 'python'
type: 'variable'
navigation:
    title: 'IN'
    icon: 'i-codicon-symbol-variable'
    level: 2
---

```python
IN = "$in"
```
::

In array

### NIN
::reference-header
---
description: >
    Not in array
lang: 'python'
type: 'variable'
navigation:
    title: 'NIN'
    icon: 'i-codicon-symbol-variable'
    level: 2
---

```python
NIN = "$nin"
```
::

Not in array

### REGEX
::reference-header
---
description: >
    Regular expression
lang: 'python'
type: 'variable'
navigation:
    title: 'REGEX'
    icon: 'i-codicon-symbol-variable'
    level: 2
---

```python
REGEX = "$regex"
```
::

Regular expression

### EXISTS
::reference-header
---
description: >
    Field exists
lang: 'python'
type: 'variable'
navigation:
    title: 'EXISTS'
    icon: 'i-codicon-symbol-variable'
    level: 2
---

```python
EXISTS = "$exists"
```
::

Field exists

### SIZE
::reference-header
---
description: >
    Array size
lang: 'python'
type: 'variable'
navigation:
    title: 'SIZE'
    icon: 'i-codicon-symbol-variable'
    level: 2
---

```python
SIZE = "$size"
```
::

Array size

### TYPE
::reference-header
---
description: >
    Field type
lang: 'python'
type: 'variable'
navigation:
    title: 'TYPE'
    icon: 'i-codicon-symbol-variable'
    level: 2
---

```python
TYPE = "$type"
```
::

Field type

## FilterInput
::reference-header
---
description: >
    Raw filter input from the request.
lang: 'python'
type: 'class'
navigation:
    title: 'FilterInput'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
@dataclass
class FilterInput()
```

Raw filter input from the request.

## ASTNode
::reference-header
---
description: >
    Base class for AST nodes.
lang: 'python'
type: 'class'
navigation:
    title: 'ASTNode'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
@dataclass
class ASTNode()
```

Base class for AST nodes.

## FieldCondition
::reference-header
---
description: >
    A condition on a specific field.
lang: 'python'
type: 'class'
navigation:
    title: 'FieldCondition'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
@dataclass
class FieldCondition(ASTNode)
```

A condition on a specific field.

## LogicalCondition
::reference-header
---
description: >
    A logical combination of conditions.
lang: 'python'
type: 'class'
navigation:
    title: 'LogicalCondition'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
@dataclass
class LogicalCondition(ASTNode)
```

A logical combination of conditions.

## OrderNode
::reference-header
---
description: >
    Represents ordering specification.
lang: 'python'
type: 'class'
navigation:
    title: 'OrderNode'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
@dataclass
class OrderNode(ASTNode)
```

Represents ordering specification.

## FieldsNode
::reference-header
---
description: >
    Represents field projection.
lang: 'python'
type: 'class'
navigation:
    title: 'FieldsNode'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
@dataclass
class FieldsNode(ASTNode)
```

Represents field projection.

## FilterAST
::reference-header
---
description: >
    Complete filter Abstract Syntax Tree.
lang: 'python'
type: 'class'
navigation:
    title: 'FilterAST'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
@dataclass
class FilterAST()
```

Complete filter Abstract Syntax Tree.

## BackendQuery
::reference-header
---
description: >
    Protocol for backend-specific query objects.
lang: 'python'
type: 'class'
navigation:
    title: 'BackendQuery'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class BackendQuery(Protocol)
```

Protocol for backend-specific query objects.

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
def apply_where(condition: ASTNode) -> "BackendQuery"
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
def apply_order(order_nodes: List[OrderNode]) -> "BackendQuery"
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
def apply_fields(fields_node: FieldsNode) -> "BackendQuery"
```

Apply field projection to the query.

## QueryCompiler
::reference-header
---
description: >
    Abstract base class for query compilers.
lang: 'python'
type: 'class'
navigation:
    title: 'QueryCompiler'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class QueryCompiler(ABC)
```

Abstract base class for query compilers.

### compile
::reference-header
---
description: >
    Compile AST to backend-specific query.
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
def compile(ast: FilterAST) -> Any
```

Compile AST to backend-specific query.

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
@abstractmethod
def supports_backend(backend_type: str) -> bool
```

Check if this compiler supports the given backend.

## ValidationRule
::reference-header
---
description: >
    Protocol for validation rules.
lang: 'python'
type: 'class'
navigation:
    title: 'ValidationRule'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class ValidationRule(Protocol)
```

Protocol for validation rules.

### validate
::reference-header
---
description: >
    Validate a node and return list of error messages.
lang: 'python'
type: 'method'
navigation:
    title: 'validate'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def validate(node: ASTNode) -> List[str]
```

Validate a node and return list of error messages.

## SecurityPolicy
::reference-header
---
description: >
    Security policy for query execution.
lang: 'python'
type: 'class'
navigation:
    title: 'SecurityPolicy'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
@dataclass
class SecurityPolicy()
```

Security policy for query execution.

