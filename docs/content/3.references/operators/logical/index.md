---
title: 'operators.logical'
description: 'Logical operators for query building.'
navigation:
    title: 'operators.logical'
    icon: 'i-codicon-library'
---

Logical operators for query building.

## LogicalOperatorHandler
::reference-header
---
description: >
    Base class for logical operator handlers.
lang: 'python'
type: 'class'
navigation:
    title: 'LogicalOperatorHandler'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class LogicalOperatorHandler(ABC)
```

Base class for logical operator handlers.

### compile
::reference-header
---
description: >
    Compile logical operator with conditions.
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
def compile(conditions: List[Any], backend: str) -> Any
```

Compile logical operator with conditions.

## AndOperatorHandler
::reference-header
---
description: >
    Handler for $and operator.
lang: 'python'
type: 'class'
navigation:
    title: 'AndOperatorHandler'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class AndOperatorHandler(LogicalOperatorHandler)
```

Handler for $and operator.

### compile
::reference-header
---
description: >
    Compile $and operator.
lang: 'python'
type: 'method'
navigation:
    title: 'compile'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def compile(conditions: List[Any], backend: str) -> Any
```

Compile $and operator.

## OrOperatorHandler
::reference-header
---
description: >
    Handler for $or operator.
lang: 'python'
type: 'class'
navigation:
    title: 'OrOperatorHandler'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class OrOperatorHandler(LogicalOperatorHandler)
```

Handler for $or operator.

### compile
::reference-header
---
description: >
    Compile $or operator.
lang: 'python'
type: 'method'
navigation:
    title: 'compile'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def compile(conditions: List[Any], backend: str) -> Any
```

Compile $or operator.

## NorOperatorHandler
::reference-header
---
description: >
    Handler for $nor operator.
lang: 'python'
type: 'class'
navigation:
    title: 'NorOperatorHandler'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class NorOperatorHandler(LogicalOperatorHandler)
```

Handler for $nor operator.

### compile
::reference-header
---
description: >
    Compile $nor operator.
lang: 'python'
type: 'method'
navigation:
    title: 'compile'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def compile(conditions: List[Any], backend: str) -> Any
```

Compile $nor operator.

