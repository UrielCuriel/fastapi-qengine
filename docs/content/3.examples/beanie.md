---
title: Ejemplos con Beanie
---

# Ejemplos con Beanie

## Básico: filtros desde la URL

:::code-tree{default-value="app.py"}
```python [models.py]
from beanie import Document

class Product(Document):
    name: str
    category: str
    price: float
    in_stock: bool = True
```

```python [app.py]
from fastapi import FastAPI, Depends
from fastapi_qengine import create_qe_dependency
from fastapi_qengine.backends.beanie import BeanieQueryEngine
from models import Product

app = FastAPI()

engine = BeanieQueryEngine(Product)
qe_dep = create_qe_dependency(engine)

@app.get("/products")
async def get_products(q = Depends(qe_dep)):
    query, projection_model, sort = q
    return await query.to_list()

# Ejemplos:
# /products?filter[where][price][$gt]=50
# /products?filter={"where":{"$or":[{"category":"electronics"},{"price":{"$lt":20}}]}}
```
:::

## Con paginación (fastapi-pagination)

:::code-tree{default-value="app.py"}
```python [models.py]
from beanie import Document

class Product(Document):
    name: str
    category: str
    price: float
```

```python [app.py]
from fastapi import FastAPI, Depends
from fastapi_qengine import create_qe_dependency
from fastapi_qengine.backends.beanie import BeanieQueryEngine
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.beanie import apaginate
from models import Product

app = FastAPI()

engine = BeanieQueryEngine(Product)
qe_dep = create_qe_dependency(engine)

@app.get("/products", response_model=Page[Product])
async def list_products(q = Depends(qe_dep)):
    beanie_query, projection_model, sort = q
    return await apaginate(beanie_query, projection_model=projection_model, sort=sort)

add_pagination(app)

# Ejemplos:
# /products?filter[where][category]=books
# /products?filter={"where":{"price":{"$gte":10,"$lte":50}},"order":"-price"}
```
:::
