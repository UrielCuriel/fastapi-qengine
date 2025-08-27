---
title: 'core.config'
description: 'Configuration settings for fastapi-qengine.'
navigation:
    title: 'core.config'
    icon: 'i-codicon-library'
---

Configuration settings for fastapi-qengine.

## ParserConfig
::reference-header
---
description: >
    Configuration for the filter parser.
lang: 'python'
type: 'class'
navigation:
    title: 'ParserConfig'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
@dataclass
class ParserConfig()
```

Configuration for the filter parser.

### strict_mode
::reference-header
---
description: >
    Whether to be strict about unknown keys
lang: 'python'
type: 'variable'
typing: 'bool'
navigation:
    title: 'strict_mode'
    icon: 'i-codicon-symbol-variable'
    level: 2
---

```python
strict_mode: bool = False
```
::

Whether to be strict about unknown keys

## ValidatorConfig
::reference-header
---
description: >
    Configuration for the filter validator.
lang: 'python'
type: 'class'
navigation:
    title: 'ValidatorConfig'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
@dataclass
class ValidatorConfig()
```

Configuration for the filter validator.

## OptimizerConfig
::reference-header
---
description: >
    Configuration for the AST optimizer.
lang: 'python'
type: 'class'
navigation:
    title: 'OptimizerConfig'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
@dataclass
class OptimizerConfig()
```

Configuration for the AST optimizer.

## CacheConfig
::reference-header
---
description: >
    Configuration for caching.
lang: 'python'
type: 'class'
navigation:
    title: 'CacheConfig'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
@dataclass
class CacheConfig()
```

Configuration for caching.

### ttl_seconds
::reference-header
---
description: >
    5 minutes
lang: 'python'
type: 'variable'
typing: 'int'
navigation:
    title: 'ttl_seconds'
    icon: 'i-codicon-symbol-variable'
    level: 2
---

```python
ttl_seconds: int = 300
```
::

5 minutes

## QEngineConfig
::reference-header
---
description: >
    Main configuration for fastapi-qengine.
lang: 'python'
type: 'class'
navigation:
    title: 'QEngineConfig'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

```python
@dataclass
class QEngineConfig()
```

Main configuration for fastapi-qengine.

### get_backend_setting
::reference-header
---
description: >
    Get a backend-specific setting.
lang: 'python'
type: 'method'
navigation:
    title: 'get_backend_setting'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def get_backend_setting(backend: str, key: str, default=None)
```

Get a backend-specific setting.

### set_backend_setting
::reference-header
---
description: >
    Set a backend-specific setting.
lang: 'python'
type: 'method'
navigation:
    title: 'set_backend_setting'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

```python
def set_backend_setting(backend: str, key: str, value: Any)
```

Set a backend-specific setting.

