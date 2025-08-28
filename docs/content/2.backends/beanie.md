---
title: Beanie / PyMongo
---

# Backend Beanie/PyMongo

::u-card
La librería incluye un backend listo para usar con Beanie/PyMongo. La compilación se basa en dos piezas:

- `BeanieQueryCompiler`: extiende `BaseQueryCompiler` y transforma el AST en componentes MongoDB.
- `BeanieQueryAdapter`: compone `filter`, `sort` y `projection` y los devuelve como `dict` listo para usar.
::

## Flujo de compilación

::steps
### apply_where
Compila nodos a operadores MongoDB (`$gt`, `$in`, `$and/$or`).

### apply_order
Traduce `order` a `[(campo, 1|-1)]`.

### apply_fields
Construye proyección `{campo: 1}`.

### finalize_query
Retorna `{"filter": ..., "sort": ..., "projection": ...}`.
::

## Uso con engine explícito

- Cada backend expone su engine; en Beanie: `BeanieQueryEngine`.
- Helper: `compile_to_mongodb(ast)` devuelve directamente los componentes MongoDB.

Ejemplo con FastAPI + Beanie

```python [routes.py]
from fastapi import FastAPI, Depends
from beanie import Document
from fastapi_qengine import create_qe_dependency
from fastapi_qengine.backends.beanie import BeanieQueryEngine

class Product(Document):
    name: str
    category: str
    price: float

app = FastAPI()

engine = BeanieQueryEngine(Product)
qe_dep = create_qe_dependency(engine)

@app.get("/products")
async def list_products(q = Depends(qe_dep)):
    # q -> (query, projection_model, sort)
    query, projection_model, sort = q
    return await query.to_list()
```

Ejemplos de entrada → salida

::code-group
```text [URL]
?filter[where][price][$gt]=50&filter[order]=-price
```
```json [Compilado]
{"filter": {"price": {"$gt": 50}}, "sort": [["price", -1]]}
```
::

::code-group
```json [JSON]
{"where": {"$or": [{"category": "electronics"}, {"price": {"$lt": 20}}]}, "fields": {"name": 1}}
```
```json [Compilado]
{"filter": {"$or": [...]}, "projection": {"name": 1}}
```
::

Notas

::alert{type="info"}
- Igualdad simple → `{campo: valor}` (sin `$eq`).
- Operadores: `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$in`, `$nin`, `$regex`, `$exists`, `$size`, `$type`; lógicos `$and`, `$or`, `$nor`.
::
