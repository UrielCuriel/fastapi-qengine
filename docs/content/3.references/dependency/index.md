---
title: 'dependency'
description: 'FastAPI dependency helpers for explicit backend engines.'
navigation:
    title: 'dependency'
    icon: 'i-codicon-library'
---

FastAPI dependency helpers para engines explícitos.

## create_qe_dependency
::reference-header
---
description: >
    Crea una dependencia FastAPI a partir de un engine explícito de backend.
lang: 'python'
type: 'function'
navigation:
    title: 'create_qe_dependency'
    icon: 'i-codicon-symbol-method'
    level: 1
---
::

```python
def create_qe_dependency(
        engine: Any,
        *,
        config: Optional[QEngineConfig] = None,
        security_policy: Optional[SecurityPolicy] = None)
```

Devuelve una función-dependencia que:

- Parsea y valida el parámetro `filter` (URL anidada o JSON string).
- Construye un `FilterAST` y lo optimiza.
- Invoca `engine.build_query(ast)` si existe, o `engine.compile(ast)` en su defecto.

Ejemplo:

```python
from fastapi_qengine import create_qe_dependency
from fastapi_qengine.backends.beanie import BeanieQueryEngine

engine = BeanieQueryEngine(Product)
qe_dep = create_qe_dependency(engine)
```

## process_filter_to_ast
::reference-header
---
description: >
    Procesa una entrada de filtro y retorna un `FilterAST` optimizado.
lang: 'python'
type: 'function'
navigation:
    title: 'process_filter_to_ast'
    icon: 'i-codicon-symbol-method'
    level: 1
---
::

```python
def process_filter_to_ast(
        filter_input: Union[str, Dict[str, Any]],
        config: Optional[QEngineConfig] = None,
        security_policy: Optional[SecurityPolicy] = None) -> FilterAST
```

Permite reutilizar el pipeline del core (parseo → normalización → validación → AST → optimización)
fuera del contexto de FastAPI (ideal para tests o usos programáticos).

