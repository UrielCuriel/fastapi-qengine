---
title: Contribuir nuevos backends
---

# Contribuir nuevos backends

¿Quieres añadir soporte para otro ORM/driver? Sigue estas pautas:

## Requisitos

- Implementa una clase `QueryCompiler` (extiende `BaseQueryCompiler`).
- Crea un `Adapter` si el backend necesita componer consulta + metadatos (orden, proyección).
- Registra el backend con `compiler_registry.register_compiler("nombre", ClaseCompiler)`.

## Alcance mínimo

- `where`: igualdad, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$in`, `$nin`.
- `order`: múltiples campos, asc/desc con `-campo`.
- `fields`: proyección de inclusión.

## Testing

- Añade tests en `tests/` (unitarios para el compiler y de integración si aplica).
- Mantén o mejora la cobertura (`pytest --cov=fastapi_qengine`).

## Documentación

- Actualiza esta sección con peculiaridades del backend (nulos, regex, joins, etc.).
- Incluye ejemplos breves de uso en FastAPI.

## PR Checklist

::u-card
- Descripción clara, escenarios cubiertos, referencias a issues.
- CI verde, sin regresiones de cobertura, changelog en README si hay cambios de API.
::
