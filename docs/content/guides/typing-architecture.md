# Arquitectura del Sistema de Tipado en fastapi-qengine

## Visión General

El sistema de tipado de fastapi-qengine está diseñado para soportar múltiples backends (MongoDB/Beanie, SQLAlchemy, etc.) mientras mantiene seguridad de tipos en tiempo de compilación y máxima claridad para los desarrolladores.

## Problema Que Resuelve

### El Desafío Original

Cuando diseñas una librería que debe:
1. Soportar múltiples backends (Beanie, SQLAlchemy, etc.)
2. Mantener cada backend independiente del core
3. Compartir lógica común entre backends
4. Proporcionar type safety

Te encuentras con un problema: **cada backend devuelve tipos diferentes**.

```python
# Beanie devuelve:
BeanieQueryResult[Product] = tuple[
    AggregationQuery[Product],
    type[BaseModel] | None,
    str | list[tuple[str, int]] | None,
]

# SQLAlchemy devolvería:
SQLAlchemyQueryResult[Product] = tuple[
    Select[Product],
    type[BaseModel] | None,
]
```

### La Solución: Genéricos Dobles

En lugar de tener un único `TypeVar` para el modelo, usamos **dos** `TypeVar`s:

```python
class Engine(Protocol[T, QueryResultType]):
    """
    T: El modelo de negocio (Product, User, etc.)
    QueryResultType: El tipo específico del backend
    """
```

Esto permite que cada backend sea transparente sobre qué tipo devuelve.

## Estructura de Tipos

### Nivel 1: TypeVars Base

```python
# Covariante - permite subtipos
T = TypeVar("T", covariant=True)
QueryResultType = TypeVar("QueryResultType", covariant=True)
```

**¿Por qué covariantes?**
- Covarianza permite que un `Product` (que hereda de `BaseModel`) se use donde se espera `BaseModel`
- Proporciona flexibilidad sin comprometer seguridad

### Nivel 2: El Protocolo Engine

```python
class Engine(Protocol[T, QueryResultType]):
    """Interface común para todos los backends."""
    
    def build_query(self, ast: FilterAST) -> QueryResultType:
        """Construye query específica del backend."""
        ...
    
    def execute_query(self, ast: FilterAST) -> QueryResultType:
        """Ejecuta y retorna resultado específico del backend."""
        ...
```

**Qué proporciona:**
- Define el contrato que todo backend debe cumplir
- Específica los tipos de retorno
- Permite duck typing - cualquier clase que implemente esto es un `Engine`

### Nivel 3: Implementaciones Específicas del Backend

#### Beanie

```python
# Definir el resultado específico
BeanieQueryResult: TypeAlias = tuple[
    AggregationQuery[TDocument],
    type[BaseModel] | None,
    str | list[tuple[str, int]] | None,
]

# Implementar Engine
class BeanieQueryEngine(Generic[TDocument]):
    """
    Implementa Engine[TDocument, BeanieQueryResult[TDocument]]
    """
    
    def build_query(self, ast: FilterAST) -> BeanieQueryResult[TDocument]:
        # Construir pipeline MongoDB
        ...
```

**Relación con Protocol:**
```
BeanieQueryEngine[Product] es compatible con:
    Engine[Product, BeanieQueryResult[Product]]
```

#### SQLAlchemy (Futuro)

```python
SQLAlchemyQueryResult: TypeAlias = tuple[
    Select[TModel],
    type[BaseModel] | None,
]

class SQLAlchemyQueryEngine(Generic[TModel]):
    """
    Implementa Engine[TModel, SQLAlchemyQueryResult[TModel]]
    """
    
    def build_query(self, ast: FilterAST) -> SQLAlchemyQueryResult[TModel]:
        # Construir SELECT statement
        ...
```

### Nivel 4: Funciones Genéricas que Usan Engine

```python
def _execute_query_on_engine(
    engine: Engine[T, QueryResultType],
    ast: FilterAST | None
) -> QueryResultType:
    """
    Esta función es totalmente agnóstica del backend.
    
    Funciona con cualquier implementación de Engine:
    - BeanieQueryEngine
    - SQLAlchemyQueryEngine
    - Cualquier otro que implemente el protocol
    """
    effective_ast = ast or FilterAST()
    return engine.build_query(effective_ast)
```

### Nivel 5: Dependencias FastAPI

```python
def create_qe_dependency(
    engine: Engine[T, QueryResultType],
    *,
    config: QEngineConfig | None = None,
    security_policy: SecurityPolicy | None = None,
) -> Callable[[Request, str | None], QueryResultType | None]:
    """
    La dependencia retorna QueryResultType | None porque:
    - Retorna None si no hay filtro
    - Retorna QueryResultType si hay filtro
    """
    
    def dependency(
        request: Request,
        filter_param: str | None = filter_query,
    ) -> QueryResultType | None:
        # ...
        return engine.build_query(ast)
    
    return dependency
```

### Nivel 6: Rutas FastAPI

```python
@app.get("/products")
async def get_products(
    # El tipo aquí refleja exactamente qué backend se usa
    query_result: BeanieQueryResult[Product] | None = Depends(product_dep),
) -> list[Product]:
    if query_result is None:
        return await Product.find_all().to_list()
    
    query, projection_model, sort_spec = query_result
    return await query.to_list()
```

## Flujo de Tipos a través del Sistema

```
1. Usuario define modelo
   │
   └─> Product (Pydantic/Beanie Document)
   
2. Usuario crea engine
   │
   └─> BeanieQueryEngine(Product)
       └─> Tipo implícito: Engine[Product, BeanieQueryResult[Product]]
   
3. Usuario crea dependencia
   │
   └─> create_qe_dependency(engine)
       └─> Retorna: Callable[..., BeanieQueryResult[Product] | None]
   
4. Usuario usa en ruta
   │
   └─> @app.get("/products")
       └─> query_result: BeanieQueryResult[Product] | None
           └─> IDE/Type Checker valida que desempaquemos correctamente
```

## Ventajas de Este Diseño

### 1. Verificación de Tipos en Tiempo de Compilación

```python
# ✅ VÁLIDO - tipo checker aprueba
async def get_products(
    query_result: BeanieQueryResult[Product] | None = Depends(product_dep),
):
    if query_result:
        query, projection_model, sort_spec = query_result  # ✅ OK

# ❌ INVÁLIDO - tipo checker rechaza
async def get_products(
    query_result: BeanieQueryResult[Product] = Depends(product_dep),  # ❌ Falta | None
):
    query, projection_model, sort_spec = query_result  # ❌ Posible None
```

### 2. Autocompletado en el IDE

```python
query_result: BeanieQueryResult[Product] | None = Depends(product_dep)

if query_result:
    query, projection_model, sort_spec = query_result
    
    # IDE sabe exactamente qué es 'query'
    # Puede sugerir métodos de AggregationQuery[Product]
    await query.to_list()  # ✅ Autocompletado disponible
```

### 3. Extensibilidad Limpia

```python
# Para agregar nuevo backend, solo necesitas:
# 1. Definir tu QueryResultType
# 2. Implementar Engine[T, QueryResultType]
# 3. Los usuarios de tu backend usan los mismos patrones
```

### 4. Documentación Viva

```python
# Los tipos son documentación ejecutable
def create_qe_dependency(
    engine: Engine[T, QueryResultType],  # De aquí sé qué tipos existen
    *,
    config: QEngineConfig | None = None,
    security_policy: SecurityPolicy | None = None,
) -> Callable[[Request, str | None], QueryResultType | None]:  # Sé qué retorna
```

## Decisiones de Diseño

### 1. ¿Por qué Protocols en lugar de Clases Base Abstractas?

**Protocols:**
- Duck typing: cualquier clase con los métodos correctos es un Engine
- No necesita herencia explícita
- Más flexible para código legacy

**Alternativa (Clases Base):**
```python
class Engine(ABC, Generic[T, QueryResultType]):
    @abstractmethod
    def build_query(self, ast: FilterAST) -> QueryResultType: ...
```

Elegimos Protocols porque:
- Ya existe `BeanieQueryEngine(Generic[TDocument])` - cambiar a heredar de `Engine` sería intruso
- Protocols permiten que código legacy implemente automáticamente la interfaz
- Es más pythónico (duck typing)

### 2. ¿Por qué QueryResultType es Covariante?

```python
QueryResultType = TypeVar("QueryResultType", covariant=True)
```

Covarianza permite:
```python
class BaseResult: pass
class SpecificResult(BaseResult): pass

# Covariante permite esto:
engine: Engine[Product, BaseResult] = engine_returning_specific  # ✅ OK
```

Sin covarianza, esto fallaría. Covarianza es segura aquí porque `QueryResultType` solo aparece como tipo de retorno (varianza out).

### 3. ¿Por qué | None en el tipo de la dependencia?

```python
async def get_products(
    query_result: BeanieQueryResult[Product] | None = Depends(qe_dep),
):
```

Porque:
- `create_qe_dependency` retorna `None` cuando no hay filtro
- Es mejor que tener que comprobar `isinstance()` dentro
- Type checker te obliga a manejar el caso `None`
- Es semánticamente correcto

## Flujo Alternativo: Sin Tipado Explícito

Si un usuario no quiere usar type hints:

```python
# Sigue funcionando, pero pierdes type safety
@app.get("/products")
async def get_products(query_result = Depends(product_dep)):
    if query_result:
        query, projection_model, sort_spec = query_result
        return await query.to_list()
    return await Product.find_all().to_list()
```

Python permite esto, pero rechazamos esta práctica en la documentación oficial.

## Comparación con Alternativas

### Alternativa 1: Usar `Any`

```python
# ❌ Malo
async def get_products(
    query_result: Any = Depends(product_dep),
):
```

Problemas:
- Pierdes type checking
- No hay autocompletado
- Errores en runtime

### Alternativa 2: Usar solo `T`

```python
# ❌ Incompleto
class Engine(Protocol[T]):
    def build_query(self, ast: FilterAST) -> T:  # ¿T es el producto o el resultado?
```

Problemas:
- Ambiguo - ¿`T` es el resultado o el modelo?
- No puedes tipar correctamente el resultado del engine

### Alternativa 3: Union de tipos posibles

```python
# ❌ Mantenimiento pesado
QueryResult = BeanieQueryResult | SQLAlchemyQueryResult | PrismaQueryResult

class Engine(Protocol[T]):
    def build_query(self, ast: FilterAST) -> QueryResult:
```

Problemas:
- Cada backend nuevo requiere actualizar el Union
- Pierde type checking específico del backend
- Complejo de mantener

## Nuestra Solución: Lo Mejor de Ambos Mundos

```python
# ✅ Bueno
class Engine(Protocol[T, QueryResultType]):
    def build_query(self, ast: FilterAST) -> QueryResultType: ...
```

Ventajas:
- Type checker sabe exactamente qué devuelve cada backend
- Cada backend es independiente
- Agregar nuevos backends no requiere cambios en el core
- Documentación clara y ejecutable

## Conclusión

El sistema de tipado de fastapi-qengine usa genéricos dobles (`T` y `QueryResultType`) para crear una abstracción que es:

1. **Type-safe**: Errores atrapados en compilación
2. **Extensible**: Nuevos backends sin cambios en el core
3. **Clara**: Tipos son documentación
4. **Pythónica**: Usa duck typing con Protocols
5. **Backwards compatible**: Código antiguo sigue funcionando

Este es un ejemplo de cómo el sistema de tipos de Python puede usarse para crear arquitecturas flexibles pero seguras.