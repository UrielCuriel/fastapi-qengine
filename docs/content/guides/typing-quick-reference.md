# Tipado en fastapi-qengine - Referencia Rápida

## El Protocolo `Engine[T, QueryResultType]`

El core de todo el sistema de tipado en fastapi-qengine gira alrededor del protocolo `Engine`, que es genérico sobre dos tipos:

```python
class Engine(Protocol[T, QueryResultType]):
    """
    T: Tipo de modelo Pydantic (Product, User, etc.)
    QueryResultType: Tipo de resultado específico del backend
    """
    def build_query(self, ast: FilterAST) -> QueryResultType: ...
    def execute_query(self, ast: FilterAST) -> QueryResultType: ...
```

## Tipado por Backend

### Beanie/MongoDB

```python
from fastapi_qengine.backends.beanie import BeanieQueryEngine
from fastapi_qengine.backends.beanie.engine import BeanieQueryResult
from beanie import Document

class Product(Document):
    name: str
    price: float

# Engine[Product, BeanieQueryResult[Product]]
engine = BeanieQueryEngine(Product)

# En tu ruta:
@app.get("/products")
async def get_products(
    query_result: BeanieQueryResult[Product] | None = Depends(create_qe_dependency(engine))
):
    if query_result is None:
        return await Product.find_all().to_list()
    
    query, projection_model, sort_spec = query_result
    return await query.to_list()
```

### SQLAlchemy (futuro)

```python
from fastapi_qengine.backends.sqlalchemy import SQLAlchemyQueryEngine
from fastapi_qengine.backends.sqlalchemy.engine import SQLAlchemyQueryResult
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    name: str
    price: float

# Engine[Product, SQLAlchemyQueryResult[Product]]
engine = SQLAlchemyQueryEngine(Product)

# En tu ruta:
@app.get("/products")
async def get_products(
    query_result: SQLAlchemyQueryResult[Product] | None = Depends(create_qe_dependency(engine))
):
    if query_result is None:
        return session.query(Product).all()
    
    select_stmt, projection_model = query_result
    return session.execute(select_stmt).scalars().all()
```

## Patrones Comunes

### Pattern 1: Crear engine sin especificar tipos explícitamente

```python
from fastapi_qengine.backends.beanie import BeanieQueryEngine

engine = BeanieQueryEngine(Product)
# Los tipos se infieren automáticamente:
# T = Product
# QueryResultType = BeanieQueryResult[Product]
```

### Pattern 2: Tipar la dependencia correctamente

```python
from fastapi import Depends
from fastapi_qengine import create_qe_dependency
from fastapi_qengine.backends.beanie.engine import BeanieQueryResult

qe_dep = create_qe_dependency(engine)

@app.get("/products")
async def get_products(
    # Siempre usa | None porque la dependencia retorna None si no hay filtro
    query_result: BeanieQueryResult[Product] | None = Depends(qe_dep)
):
    ...
```

### Pattern 3: Manejar múltiples backends en el mismo proyecto

```python
from fastapi_qengine.backends.beanie import BeanieQueryEngine
from fastapi_qengine.backends.beanie.engine import BeanieQueryResult as BeanieResult

from fastapi_qengine.backends.sqlalchemy import SQLAlchemyQueryEngine
from fastapi_qengine.backends.sqlalchemy.engine import SQLAlchemyQueryResult as SQLResult

# Beanie
product_engine = BeanieQueryEngine(Product)
product_dep = create_qe_dependency(product_engine)

@app.get("/products")
async def get_products(
    query_result: BeanieResult[Product] | None = Depends(product_dep)
):
    ...

# SQLAlchemy
user_engine = SQLAlchemyQueryEngine(User)
user_dep = create_qe_dependency(user_engine)

@app.get("/users")
async def get_users(
    query_result: SQLResult[User] | None = Depends(user_dep)
):
    ...
```

## TypeVars en el Sistema

```python
# Definidos en fastapi_qengine.core.types

T = TypeVar("T", covariant=True)
# Representa el modelo Pydantic
# Covariante: Product es subtipo de BaseModel

QueryResultType = TypeVar("QueryResultType", covariant=True)
# Representa el tipo de resultado del backend
# Covariante: permite flexibilidad en la jerarquía de tipos
```

## Lo Que NO Hacer

❌ Olvidar el `| None`:
```python
# MALO - la dependencia retorna None si no hay filtro
async def get_products(
    query_result: BeanieQueryResult[Product] = Depends(qe_dep)  # ❌ No compatible
):
```

❌ Usar `Any`:
```python
# MALO - pierde type safety
async def get_products(
    query_result: Any = Depends(qe_dep)
):
```

❌ Desempacar sin comprobar None:
```python
# MALO - crash si query_result es None
async def get_products(
    query_result: BeanieQueryResult[Product] | None = Depends(qe_dep)
):
    query, _, _ = query_result  # ❌ Crash si None
```

## Checklist de Tipado

- [ ] ¿Especificaste `| None` en el tipo de la dependencia?
- [ ] ¿Importaste el `QueryResultType` correcto del backend?
- [ ] ¿Verificas si `query_result is None` antes de desempacar?
- [ ] ¿El modelo que pasas a `BeanieQueryEngine(Product)` es el correcto?
- [ ] ¿Tu IDE muestra type hints correctos al hover sobre las variables?

## Referencias

- [Guía Completa de Tipado](./typing-guide.md)
- [Documentación de Engine Protocol](../3.references/core/types.md)
- [Ejemplos de Uso](../../examples/)