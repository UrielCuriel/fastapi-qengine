---
title: Backend personalizado con SQLAlchemy
---

# Backend personalizado con SQLAlchemy

::alert{type="warning" icon="i-lucide-flask-round"}
Ejemplo educativo: no forma parte del paquete. Úsalo como base para tu implementación real.
::

Esta guía muestra cómo crear un backend para SQLAlchemy implementando un `QueryCompiler` propio y exponiendo un engine explícito (sin registro global).

## Pasos

1) Crea `fastapi_qengine/backends/sqlalchemy.py` con un `SQLAlchemyQueryCompiler` que extienda `BaseQueryCompiler`.
2) Implementa un `Adapter` mínimo que componga un `select()` con filtros, orden y proyección.
3) Crea `SqlAlchemyQueryEngine` que use el compiler para construir el query final.
4) Úsalo en FastAPI: `create_qe_dependency(SqlAlchemyQueryEngine(YourModel))`.

## Ejemplo mínimo

::details{summary="Compiler mínimo (ejemplo)"}
```python [fastapi_qengine/backends/sqlalchemy.py]
# fastapi_qengine/backends/sqlalchemy.py
from typing import Any, Dict, List
from sqlalchemy import and_, or_, select
from ..core.compiler_base import BaseQueryCompiler
from ..core.types import FieldCondition, LogicalCondition, FieldsNode, OrderNode

class SQLAlchemyQueryCompiler(BaseQueryCompiler):
    def __init__(self, model):
        super().__init__("sqlalchemy")
        self.model = model
        self._stmt = select(self.model)

    def create_base_query(self):
        return self._stmt

    def apply_where(self, stmt, where_node):
        return stmt.where(self._compile_condition(where_node))

    def apply_order(self, stmt, order_nodes: List[OrderNode]):
        clauses = [getattr(self.model, o.field).asc() if o.ascending else getattr(self.model, o.field).desc() for o in order_nodes]
        return stmt.order_by(*clauses)

    def apply_fields(self, stmt, fields_node: FieldsNode):
        cols = [getattr(self.model, k) for k, v in fields_node.fields.items() if v == 1]
        return select(*cols).select_from(self.model).where(*stmt._where_criteria)  # simple proyección

    # Compilación básica de condiciones
    def _compile_condition(self, node):
        if isinstance(node, FieldCondition):
            col = getattr(self.model, node.field)
            op = node.operator.value
            v = node.value
            return {
                "$eq": col == v,
                "$ne": col != v,
                "$gt": col > v,
                "$gte": col >= v,
                "$lt": col < v,
                "$lte": col <= v,
                "$in": col.in_(v),
                "$nin": ~col.in_(v),
            }[op]
        elif isinstance(node, LogicalCondition):
            compiled = [self._compile_condition(n) for n in node.conditions]
            return and_(*compiled) if node.operator.value == "$and" else or_(*compiled)
        raise ValueError("Tipo de nodo no soportado")
```
::

Uso en FastAPI:

```python [usage.py]
from fastapi_qengine import create_qe_dependency
from fastapi_qengine.backends.sqlalchemy import SqlAlchemyQueryEngine

engine = SqlAlchemyQueryEngine(Product)
qe_dep = create_qe_dependency(engine)
```

::alert{type="info"}
- Puedes reutilizar `operators` para mapear operadores por backend.
- Implementa tests de integración en `tests/` para validar filtros, orden y proyección.
::
