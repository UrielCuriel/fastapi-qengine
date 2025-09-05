---
title: 'core.errors'
description: 'Custom exceptions for fastapi-qengine.'
navigation:
    title: 'core.errors'
    icon: 'i-codicon-library'
---

Custom exceptions for fastapi-qengine.

## QEngineError
::reference-header
---
description: >
    Base exception for all fastapi-qengine errors.
lang: 'python'
type: 'class'
navigation:
    title: 'QEngineError'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class QEngineError(Exception)
```

Base exception for all fastapi-qengine errors.

## ParseError
::reference-header
---
description: >
    Raised when filter parsing fails.
lang: 'python'
type: 'class'
navigation:
    title: 'ParseError'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class ParseError(QEngineError)
```

Raised when filter parsing fails.

## ValidationError
::reference-header
---
description: >
    Raised when filter validation fails.
lang: 'python'
type: 'class'
navigation:
    title: 'ValidationError'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class ValidationError(QEngineError)
```

Raised when filter validation fails.

## SecurityError
::reference-header
---
description: >
    Raised when security policy is violated.
lang: 'python'
type: 'class'
navigation:
    title: 'SecurityError'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class SecurityError(QEngineError)
```

Raised when security policy is violated.

## CompilerError
::reference-header
---
description: >
    Raised when AST compilation fails.
lang: 'python'
type: 'class'
navigation:
    title: 'CompilerError'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class CompilerError(QEngineError)
```

Raised when AST compilation fails.

## UnsupportedOperatorError
::reference-header
---
description: >
    Raised when an unsupported operator is used.
lang: 'python'
type: 'class'
navigation:
    title: 'UnsupportedOperatorError'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class UnsupportedOperatorError(QEngineError)
```

Raised when an unsupported operator is used.

## RegistryError
::reference-header
---
description: >
    Raised when registry operations fail.
lang: 'python'
type: 'class'
navigation:
    title: 'RegistryError'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class RegistryError(QEngineError)
```

Raised when registry operations fail.

## OptimizationError
::reference-header
---
description: >
    Raised when AST optimization fails.
lang: 'python'
type: 'class'
navigation:
    title: 'OptimizationError'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
class OptimizationError(QEngineError)
```

Raised when AST optimization fails.

