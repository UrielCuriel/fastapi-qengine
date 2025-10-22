# Diagramas de Flujo del Sistema de Tipado

## 1. Arquitectura de Tipos por Capas

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Route Handler                    │
│  query_result: BeanieQueryResult[Product] | None            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Dependency (create_qe_dependency)      │
│  Retorna: QueryResultType | None                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│          Engine Protocol (Genérico sobre 2 tipos)           │
│  Engine[T, QueryResultType]                                 │
│  - build_query(ast: FilterAST) -> QueryResultType           │
│  - execute_query(ast: FilterAST) -> QueryResultType         │
└──────────────────────────┬──────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
    ┌─────────┐      ┌─────────┐      ┌─────────┐
    │ Beanie  │      │SQLAlch. │      │ Prisma  │
    │ Backend │      │ Backend │      │ Backend │
    └─────────┘      └─────────┘      └─────────┘
         │                 │                 │
         ▼                 ▼                 ▼
    ┌──────────┐    ┌───────────┐    ┌─────────┐
    │BeanieQR  │    │SQLAlchQR  │    │PrismaQR │
    │[Product] │    │[Product]  │    │[Product]│
    └──────────┘    └───────────┘    └─────────┘
```

## 2. Flujo de Tipos desde Request hasta Response

```
HTTP Request
   │
   ├─ /products?filter={"where":{"price":{"$gt":50}}}
   │
   ▼
┌──────────────────────────────────────────┐
│  FastAPI extrae parámetros               │
│  request: Request                        │
│  filter_param: str | None                │
└──────────────────────────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ dependency function  │
                    └──────────────────────┘
                               │
                               ▼
            ┌──────────────────────────────────────────┐
            │ _get_filter_input_from_request           │
            │ Retorna: str | dict[str, object] | None  │
            └──────────────────────┬───────────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │ process_filter_to_ast        │
                    │ Retorna: FilterAST           │
                    └──────────────────┬───────────┘
                                       │
                                       ▼
                ┌──────────────────────────────────────┐
                │ _execute_query_on_engine             │
                │ engine: Engine[T, QueryResultType]   │
                │ ast: FilterAST | None                │
                └──────────────┬─────────────────────┘
                               │
                               ▼
                ┌──────────────────────────────────┐
                │ engine.build_query(ast)          │
                │ Retorna: QueryResultType         │
                └──────────────┬────────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
    ┌────────────┐        ┌──────────┐        ┌──────────┐
    │BeanieQR   │        │SQLAlchQR │        │PrismaQR  │
    │Beanie DB  │        │SQL DB    │        │Prisma DB │
    └────────────┘        └──────────┘        └──────────┘
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ query_result         │
                    │ QueryResultType | None
                    └──────────┬───────────┘
                               │
                               ▼
                ┌──────────────────────────────┐
                │ Handler desempaca la tupla    │
                │ query, projection, sort_spec │
                └──────────────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────┐
                        │ Ejecuta query    │
                        │ Retorna resultados
                        └──────────┬───────┘
                                   │
                                   ▼
                          HTTP Response
                          200 OK
                          [{"id": 1, ...}]
```

## 3. Matriz de Tipos por Backend

```
┌─────────────────┬──────────────────────┬──────────────────────┐
│    Backend      │    QueryResultType   │   Ejemplo Completo   │
├─────────────────┼──────────────────────┼──────────────────────┤
│ Beanie/MongoDB  │ BeanieQueryResult    │ Engine[Product,      │
│                 │ [TDocument]          │ BeanieQueryResult    │
│                 │                      │ [Product]]           │
├─────────────────┼──────────────────────┼──────────────────────┤
│ SQLAlchemy      │ SQLAlchemyQR         │ Engine[Product,      │
│                 │ [TModel]             │ SQLAlchemyQR         │
│                 │                      │ [Product]]           │
├─────────────────┼──────────────────────┼──────────────────────┤
│ Prisma          │ PrismaQueryResult    │ Engine[Product,      │
│                 │ [TModel]             │ PrismaQueryResult    │
│                 │                      │ [Product]]           │
├─────────────────┼──────────────────────┼──────────────────────┤
│ Tortoise ORM    │ TortoiseQueryResult  │ Engine[Product,      │
│                 │ [TModel]             │ TortoiseQueryResult  │
│                 │                      │ [Product]]           │
└─────────────────┴──────────────────────┴──────────────────────┘
```

## 4. Jerarquía de Generics

```
TypeVar Base
   │
   ├─ T (covariant)
   │  │
   │  ├─ Modelo Pydantic
   │  ├─ Modelo Beanie Document
   │  └─ Modelo SQLAlchemy Declarative
   │
   └─ QueryResultType (covariant)
      │
      ├─ BeanieQueryResult[T]
      │  └─ tuple[AggregationQuery[T], type[BaseModel] | None, str | list | None]
      │
      ├─ SQLAlchemyQueryResult[T]
      │  └─ tuple[Select[T], type[BaseModel] | None]
      │
      └─ PrismaQueryResult[T]
         └─ tuple[PrismaQuery, type[BaseModel] | None]
```

## 5. Flujo de Type Inference

```
Código del Usuario:
────────────────────────────────────────────

engine = BeanieQueryEngine(Product)
   │
   ├─ BeanieQueryEngine es Generic[TDocument]
   ├─ Se instancia con Product
   └─ Type: BeanieQueryEngine[Product]
           Implícitamente: Engine[Product, BeanieQueryResult[Product]]


qe_dep = create_qe_dependency(engine)
   │
   ├─ create_qe_dependency acepta Engine[T, QueryResultType]
   ├─ Infiere: T = Product, QueryResultType = BeanieQueryResult[Product]
   └─ Type: Callable[[Request, str | None], BeanieQueryResult[Product] | None]


@app.get("/products")
async def get_products(
    query_result: BeanieQueryResult[Product] | None = Depends(qe_dep)
):
   │
   ├─ Typer checker valida que BeanieQueryResult[Product] | None
   │  es compatible con Callable's return type
   └─ ✅ Todo validado
```

## 6. Desempaque de Tupla Tipada

```
query_result: BeanieQueryResult[Product] | None
    │
    ├─ Si None: Sin filtro proporcionado
    │
    └─ Si BeanieQueryResult[Product]:
       │
       ├─ query: AggregationQuery[Product]
       │  └─ Métodos disponibles: to_list(), count(), etc.
       │
       ├─ projection_model: type[BaseModel] | None
       │  └─ Modelo generado para proyecciones
       │
       └─ sort_spec: str | list[tuple[str, int]] | None
          └─ Especificación de ordenamiento
```

## 7. Decisión de Tipado: Covariancia

```
Definición:
───────────
T = TypeVar("T", covariant=True)
QueryResultType = TypeVar("QueryResultType", covariant=True)

Implicación:
────────────
class Engine(Protocol[T, QueryResultType]):
    def build_query(self, ast: FilterAST) -> QueryResultType:
        ...

Porque son covariant (solo como return type):

    Product ⊆ BaseModel
         │
         ▼
BeanieQueryResult[Product] ⊆ BeanieQueryResult[BaseModel]

Permite:
    engine: Engine[BaseModel, QueryResultType] = engine_product  ✅
```

## 8. Evolución de la Arquitectura de Tipado

```
Versión 1 (Inicial)
───────────────────
class Engine(Protocol[T]):
    def build_query(self, ast: FilterAST): ...

Problema: ¿T es el modelo o el resultado?


Versión 2 (Actual - Tu Solución)
─────────────────────────────────
class Engine(Protocol[T, QueryResultType]):
    def build_query(self, ast: FilterAST) -> QueryResultType: ...

Beneficio: T y QueryResultType tienen