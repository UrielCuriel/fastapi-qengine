# Guía de Tipado en fastapi-qengine

## Introducción

fastapi-qengine utiliza un sistema de tipado flexible basado en genéricos de Python para soportar múltiples backends (Beanie/MongoDB, SQLAlchemy, etc.) mientras mantiene una interfaz común. Esta guía explica cómo tipar correctamente el código al usar fastapi-qengine.

## Concepto Fundamental: El Protocolo `Engine`

El protocolo `Engine` es la abstracción central que define la interfaz para todos los backends. Es genérico sobre **dos tipos**:

```python
from fastapi_qengine.core.types import Engine

class Engine(Protocol[T, QueryResultType]):
    """
    T: El tipo de modelo Pydantic utilizado para validación y proyección.
    QueryResultType: El tipo de resultado específico del backend.
    """
    def build_query(self, ast: FilterAST) -> QueryResultType:
        """Construye una consulta desde un AST."""
        ...

    def execute_query(self, ast: FilterAST) -> QueryResultType:
        """Ejecuta la consulta y retorna el resultado."""
        ...
```

## Los Dos TypeVars Genéricos

### 1. `T` - El Modelo Pydantic

Es el modelo que representa los documentos/registros en tu base de datos:

```python
from pydantic import BaseModel

class Product(BaseModel):
    """Modelo que representa un producto."""
    name: str
    price: float
    category: str
```

Cuando usas fastapi-qengine, `T` es tu modelo Pydantic:

```python
engine = BeanieQueryEngine(Product)  # T = Product
```

### 2. `QueryResultType` - El Tipo de Resultado del Backend

Cada backend devuelve un tipo de resultado diferente. Por ejemplo:

#### Beanie/MongoDB

```python
from fastapi_qengine.backends.beanie.engine import BeanieQueryResult

# BeanieQueryResult es una tupla específica de Beanie
BeanieQueryResult[Product] = tuple[
    AggregationQuery[Product],
    type[BaseModel] | None,
    str | list[tuple[str, int]] | None,
]
```

#### SQLAlchemy (futuro)

```python
SQLAlchemyQueryResult[Product] = tuple[
    Select[Product],
    type[BaseModel] | None,
]
```

## Tipado Correcto de `create_qe_dependency`

La función `create_qe_dependency` retorna una función FastAPI que depende de los dos genéricos del `Engine`:

```python
from typing import Callable
from fastapi import Request
from fastapi_qengine.core.types import Engine

def create_qe_dependency(
    engine: Engine[T, QueryResultType],
    *,
    config: QEngineConfig | None = None,
    security_policy: SecurityPolicy | None = None,
) -> Callable[[Request, str | None], QueryResultType | None]:
    """
    Retorna una dependencia de FastAPI.
    
    El tipo de retorno es QueryResultType | None porque:
    - Si no hay filtro en la request, retorna None
    - Si hay filtro, retorna el QueryResultType específico del backend
    """
    ...
```

## Ejemplo Práctico Completo

### Paso 1: Definir tu modelo

```python
from beanie import Document
from pydantic import BaseModel

class Product(Document):
    """Modelo Beanie para productos."""
    name: str
    price: float
    category: str
    in_stock: bool
```

### Paso 2: Crear el engine

```python
from fastapi_qengine.backends.beanie import BeanieQueryEngine

# Aquí T = Product
# QueryResultType = BeanieQueryResult[Product]
engine = BeanieQueryEngine(Product)
```

### Paso 3: Crear la dependencia

```python
from fastapi_qengine import create_qe_dependency
from fastapi_qengine.backends.beanie.engine import BeanieQueryResult

# La dependencia retorna BeanieQueryResult[Product] | None
qe_dep = create_qe_dependency(engine)
```

### Paso 4: Usar en una ruta FastAPI

```python
from fastapi import FastAPI, Depends

app = FastAPI()

@app.get("/products")
async def get_products(
    # Tipo: BeanieQueryResult[Product] | None
    query_result: BeanieQueryResult[Product] | None = Depends(qe_dep),
) -> list[Product]:
    """
    La dependencia inyecta:
    - None si no hay filtro en la query string
    - BeanieQueryResult[Product] si hay filtro
    """
    if query_result is None:
        # Sin filtro - retorna todo
        return await Product.find_all().to_list()
    
    # Con filtro - desempaca la tupla
    query, projection_model, sort_spec = query_result
    return await query.to_list()
```

## Manejo de Diferentes Backends

Cuando agregues un nuevo backend, debes:

1. **Definir tu `QueryResultType`** específico:

```python
# sqlalchemy_engine.py
SQLAlchemyQueryResult: TypeAlias = tuple[
    Select[TModel],
    type[BaseModel] | None,
]

class SQLAlchemyQueryEngine(Generic[TModel]):
    def build_query(self, ast: FilterAST) -> SQLAlchemyQueryResult[TModel]:
        ...
```

2. **Tipar correctamente en dependencias**:

```python
from fastapi_qengine.backends.sqlalchemy.engine import SQLAlchemyQueryResult

@app.get("/products")
async def get_products(
    query_result: SQLAlchemyQueryResult[Product] | None = Depends(qe_dep),
):
    if query_result is None:
        return session.execute(select(Product)).scalars().all()
    
    select_stmt, projection_model = query_result
    return session.execute(select_stmt).scalars().all()
```

## Ventajas de Este Diseño

1. **Type Safety**: El IDE y mypy/pyright detectan errores de tipado
2. **Backend Agnostic**: Tu código es agnóstico al backend específico
3. **Explicititud**: Es claro qué tipo devuelve cada backend
4. **Extensibilidad**: Agregar nuevos backends es straightforward

## Anti-patrones Comunes

❌ **MAL: Usar `Any` o tipos genéricos sin especificar**

```python
# Pierde type safety
query_result: Any = Depends(qe_dep)
```

❌ **MAL: Asumir que siempre es una tupla sin comprobar None**

```python
@app.get("/products")
async def get_products(
    query_result: BeanieQueryResult[Product] = Depends(qe_dep),  # ❌ No puede ser None
):
    query, _, _ = query_result  # ❌ Crash si query_result es None
```

✅ **BIEN: Manejar el caso None explícitamente**

```python
@app.get("/products")
async def get_products(
    query_result: BeanieQueryResult[Product] | None = Depends(qe_dep),
) -> list[Product]:
    if query_result is None:
        return await Product.find_all().to_list()
    
    query, _, _ = query_result
    return await query.to_list()
```

## TypeVars en fastapi-qengine

### `T` (covariant)

```python
T = TypeVar("T", covariant=True)
```

Se usa para el modelo base. Es covariante porque un subtype de `Product` puede usarse donde se espera `Product`.

### `QueryResultType` (covariant)

```python
QueryResultType = TypeVar("QueryResultType", covariant=True)
```

Se usa para el tipo de resultado específico del backend. También es covariante por flexibilidad.

## Resumen

| Concepto | Tipo | Ejemplo |
|----------|------|---------|
| Modelo Pydantic | `T` | `Product` (BaseModel o Document) |
| Resultado del Backend | `QueryResultType` | `BeanieQueryResult[Product]` |
| Engine | `Engine[T, QueryResultType]` | `BeanieQueryEngine[Product]` |
| Dependencia FastAPI | `Callable[..., QueryResultType \| None]` | Retorna tupla o None |

Este diseño permite que fastapi-qengine sea flexible y extensible mientras mantiene seguridad de tipos robusta.