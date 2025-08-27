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
from fastapi_qengine import QueryEngine
from models import Product

app = FastAPI()

@app.get("/products")
async def get_products(query = Depends(QueryEngine(Product))):
    q = Product.find(query.get("filter"))
    if "sort" in query:
        q = q.sort(query["sort"])  # [("price", -1)]
    if "projection" in query:
        q = q.project(**query["projection"])  # {"name": 1, ...}
    return await q.to_list()

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
from fastapi_qengine import QueryEngine
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.beanie import apaginate
from models import Product

app = FastAPI()

@app.get("/products", response_model=Page[Product])
async def list_products(query = Depends(QueryEngine(Product))):
    q = Product.find(query.get("filter"))
    if "sort" in query:
        q = q.sort(query["sort"])  # opcional
    return await apaginate(q)

add_pagination(app)

# Ejemplos:
# /products?filter[where][category]=books
# /products?filter={"where":{"price":{"$gte":10,"$lte":50}},"order":"-price"}
```
:::

