---
title: 'operators.comparison'
description: 'Comparison operators for query building.'
navigation:
    title: 'operators.comparison'
    icon: 'i-codicon-library'
---

Comparison operators for query building.

## ComparisonOperatorHandler
::reference-header
---
description: >
    Base class for comparison operator handlers.
lang: 'python'
type: 'class'
navigation:
    title: 'ComparisonOperatorHandler'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class ComparisonOperatorHandler(ABC)
```

Base class for comparison operator handlers.

### compile
::reference-header
---
description: >
    Compile comparison operator with field and value.
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

Compile comparison operator with field and value.

## EqualOperatorHandler
::reference-header
---
description: >
    Handler for $eq operator.
lang: 'python'
type: 'class'
navigation:
    title: 'EqualOperatorHandler'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class EqualOperatorHandler(ComparisonOperatorHandler)
```

Handler for $eq operator.

### compile
::reference-header
---
description: >
    Compile $eq operator.
lang: 'python'
type: 'method'
navigation:
    title: 'compile'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def compile(field: str, value: Any, backend: str) -> Any
```

Compile $eq operator.

## NotEqualOperatorHandler
::reference-header
---
description: >
    Handler for $ne operator.
lang: 'python'
type: 'class'
navigation:
    title: 'NotEqualOperatorHandler'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class NotEqualOperatorHandler(ComparisonOperatorHandler)
```

Handler for $ne operator.

### compile
::reference-header
---
description: >
    Compile $ne operator.
lang: 'python'
type: 'method'
navigation:
    title: 'compile'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def compile(field: str, value: Any, backend: str) -> Any
```

Compile $ne operator.

## GreaterThanOperatorHandler
::reference-header
---
description: >
    Handler for $gt operator.
lang: 'python'
type: 'class'
navigation:
    title: 'GreaterThanOperatorHandler'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class GreaterThanOperatorHandler(ComparisonOperatorHandler)
```

Handler for $gt operator.

### compile
::reference-header
---
description: >
    Compile $gt operator.
lang: 'python'
type: 'method'
navigation:
    title: 'compile'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def compile(field: str, value: Any, backend: str) -> Any
```

Compile $gt operator.

## GreaterThanEqualOperatorHandler
::reference-header
---
description: >
    Handler for $gte operator.
lang: 'python'
type: 'class'
navigation:
    title: 'GreaterThanEqualOperatorHandler'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class GreaterThanEqualOperatorHandler(ComparisonOperatorHandler)
```

Handler for $gte operator.

### compile
::reference-header
---
description: >
    Compile $gte operator.
lang: 'python'
type: 'method'
navigation:
    title: 'compile'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def compile(field: str, value: Any, backend: str) -> Any
```

Compile $gte operator.

## LessThanOperatorHandler
::reference-header
---
description: >
    Handler for $lt operator.
lang: 'python'
type: 'class'
navigation:
    title: 'LessThanOperatorHandler'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class LessThanOperatorHandler(ComparisonOperatorHandler)
```

Handler for $lt operator.

### compile
::reference-header
---
description: >
    Compile $lt operator.
lang: 'python'
type: 'method'
navigation:
    title: 'compile'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def compile(field: str, value: Any, backend: str) -> Any
```

Compile $lt operator.

## LessThanEqualOperatorHandler
::reference-header
---
description: >
    Handler for $lte operator.
lang: 'python'
type: 'class'
navigation:
    title: 'LessThanEqualOperatorHandler'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class LessThanEqualOperatorHandler(ComparisonOperatorHandler)
```

Handler for $lte operator.

### compile
::reference-header
---
description: >
    Compile $lte operator.
lang: 'python'
type: 'method'
navigation:
    title: 'compile'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def compile(field: str, value: Any, backend: str) -> Any
```

Compile $lte operator.

## InOperatorHandler
::reference-header
---
description: >
    Handler for $in operator.
lang: 'python'
type: 'class'
navigation:
    title: 'InOperatorHandler'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class InOperatorHandler(ComparisonOperatorHandler)
```

Handler for $in operator.

### compile
::reference-header
---
description: >
    Compile $in operator.
lang: 'python'
type: 'method'
navigation:
    title: 'compile'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def compile(field: str, value: Any, backend: str) -> Any
```

Compile $in operator.

## NotInOperatorHandler
::reference-header
---
description: >
    Handler for $nin operator.
lang: 'python'
type: 'class'
navigation:
    title: 'NotInOperatorHandler'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class NotInOperatorHandler(ComparisonOperatorHandler)
```

Handler for $nin operator.

### compile
::reference-header
---
description: >
    Compile $nin operator.
lang: 'python'
type: 'method'
navigation:
    title: 'compile'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def compile(field: str, value: Any, backend: str) -> Any
```

Compile $nin operator.

## RegexOperatorHandler
::reference-header
---
description: >
    Handler for $regex operator.
lang: 'python'
type: 'class'
navigation:
    title: 'RegexOperatorHandler'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class RegexOperatorHandler(ComparisonOperatorHandler)
```

Handler for $regex operator.

### compile
::reference-header
---
description: >
    Compile $regex operator.
lang: 'python'
type: 'method'
navigation:
    title: 'compile'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def compile(field: str, value: Any, backend: str) -> Any
```

Compile $regex operator.

## ExistsOperatorHandler
::reference-header
---
description: >
    Handler for $exists operator.
lang: 'python'
type: 'class'
navigation:
    title: 'ExistsOperatorHandler'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class ExistsOperatorHandler(ComparisonOperatorHandler)
```

Handler for $exists operator.

### compile
::reference-header
---
description: >
    Compile $exists operator.
lang: 'python'
type: 'method'
navigation:
    title: 'compile'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def compile(field: str, value: Any, backend: str) -> Any
```

Compile $exists operator.

## SizeOperatorHandler
::reference-header
---
description: >
    Handler for $size operator.
lang: 'python'
type: 'class'
navigation:
    title: 'SizeOperatorHandler'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class SizeOperatorHandler(ComparisonOperatorHandler)
```

Handler for $size operator.

### compile
::reference-header
---
description: >
    Compile $size operator.
lang: 'python'
type: 'method'
navigation:
    title: 'compile'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def compile(field: str, value: Any, backend: str) -> Any
```

Compile $size operator.

## TypeOperatorHandler
::reference-header
---
description: >
    Handler for $type operator.
lang: 'python'
type: 'class'
navigation:
    title: 'TypeOperatorHandler'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class TypeOperatorHandler(ComparisonOperatorHandler)
```

Handler for $type operator.

### compile
::reference-header
---
description: >
    Compile $type operator.
lang: 'python'
type: 'method'
navigation:
    title: 'compile'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def compile(field: str, value: Any, backend: str) -> Any
```

Compile $type operator.

