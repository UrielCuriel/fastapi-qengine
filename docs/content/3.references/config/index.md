---
title: 'config'
description: 'Referencia detallada de QEngineConfig, SecurityPolicy y sub-configuraciones.'
navigation:
  title: 'config'
  icon: 'i-codicon-gear'
---

Referencia detallada para personalizar el pipeline de `fastapi-qengine`.

## QEngineConfig

- default_backend: Backend por defecto (string). No impacta engines explícitos.
- debug: Modo depuración (bool). Si `True`, errores internos se reportan con detalle.
- security_policy: Instancia `SecurityPolicy` aplicada por defecto.
- parser: `ParserConfig`.
- validator: `ValidatorConfig`.
- optimizer: `OptimizerConfig`.
- cache: `CacheConfig`.
- backend_settings: `dict[str, dict[str, Any]]` con ajustes por backend.

```python
from fastapi_qengine.core import QEngineConfig, ParserConfig, ValidatorConfig, OptimizerConfig, CacheConfig

config = QEngineConfig(
    debug=True,
    parser=ParserConfig(max_nesting_depth=8, strict_mode=False, case_sensitive_operators=True),
    validator=ValidatorConfig(validate_types=True, validate_operators=True, validate_field_names=True),
    optimizer=OptimizerConfig(enabled=True, simplify_logical_operators=True, combine_range_conditions=True),
    cache=CacheConfig(enabled=False, ttl_seconds=300, max_size=1000),
)

# Ajustes específicos del backend (p. ej., 'beanie')
config.set_backend_setting("beanie", "allow_projection_merge", True)
```

## SecurityPolicy

- max_depth: Profundidad máxima permitida para anidación lógica (`$and/$or/...`).
- allowed_operators: Lista blanca de `ComparisonOperator` permitidos. Si `None`, todos los soportados.
- allowed_fields: Lista blanca de campos permitidos. Si se define, todo campo fuera de la lista se bloquea.
- blocked_fields: Lista negra de campos siempre bloqueados.
- max_array_size: Tamaño máximo de arreglos (p. ej., para `$in`/`$nin`).

```python
from fastapi_qengine.core import SecurityPolicy, ComparisonOperator

policy = SecurityPolicy(
    max_depth=3,
    allowed_operators=[ComparisonOperator.EQ, ComparisonOperator.IN, ComparisonOperator.LTE],
    allowed_fields=["name", "category", "price"],
    blocked_fields=["internal_notes", "password"],
    max_array_size=100,
)
```

## ParserConfig

- max_nesting_depth: Límite de anidación en entrada (parser), previo a validación de seguridad.
- strict_mode: Rechaza claves/desconocidas/formato inválido tempranamente.
- case_sensitive_operators: Si `True`, `$GT` no se acepta como `$gt`.
- allow_empty_conditions: Permite `where` vacío si `True`.

## ValidatorConfig

- validate_types: Verifica tipos básicos (bool/num/array) en operadores.
- validate_operators: Verifica uso correcto de operadores.
- validate_field_names: Verifica nombres de campos no vacíos y strings.
- custom_validators: Lista de validadores extra (strings identificadores para integración avanzada).

## OptimizerConfig

- enabled: Habilita/deshabilita optimizaciones.
- simplify_logical_operators: Fusiona/limpia estructuras lógicas redundantes.
- combine_range_conditions: Combina `$gt/$gte/$lt/$lte` por campo.
- remove_redundant_conditions: Elimina condiciones duplicadas.
- max_optimization_passes: Límite de pasadas de optimización.

## CacheConfig

- enabled: Habilita caché (si tu integración lo implementa).
- ttl_seconds: TTL por entrada.
- max_size: Capacidad.
- cache_parsed_filters: Cachea entrada parseada.
- cache_compiled_queries: Cachea salida compilada.

## Integración con engines explícitos

```python
from fastapi_qengine import create_qe_dependency, process_filter_to_ast
from fastapi_qengine.core import QEngineConfig, SecurityPolicy
from fastapi_qengine.backends.beanie import BeanieQueryEngine

config = QEngineConfig(debug=True)
policy = SecurityPolicy(max_depth=3)

engine = BeanieQueryEngine(Product)
qe_dep = create_qe_dependency(engine, config=config, security_policy=policy)

# Uso programático del pipeline
ast = process_filter_to_ast({"where": {"category": "books"}}, config=config, security_policy=policy)
```

::u-alert{type="info"}
Los engines pueden leer `backend_settings` según sus necesidades. Consulta la documentación de cada backend para saber qué claves admite.
::

