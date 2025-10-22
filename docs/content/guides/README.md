# Guías de fastapi-qengine

## Tipado en fastapi-qengine

El sistema de tipado en fastapi-qengine está diseñado para soportar múltiples backends (Beanie/MongoDB, SQLAlchemy, etc.) mientras mantiene seguridad de tipos completa y código agnóstico del backend.

### Documentos Disponibles

#### 1. [TYPING_SOLUTION.md](../../TYPING_SOLUTION.md) - **COMIENZA AQUÍ**
El documento principal que responde tu pregunta sobre cómo tipar en fastapi-qengine.

**Contiene:**
- La pregunta original y su respuesta
- Implementación paso a paso
- Ejemplos de uso en rutas FastAPI
- Comparación antes/después
- Resumen de las dos dimensiones de tipado

**Para quién:** Cualquier persona que quiera entender cómo tipar `create_qe_dependency` y por qué.

---

#### 2. [typing-guide.md](./typing-guide.md) - Guía Completa
Una guía exhaustiva del sistema de tipado con conceptos fundamentales.

**Contiene:**
- Concepto fundamental del protocolo `Engine`
- Los dos `TypeVar`s genéricos explicados
- Tipado correcto de `create_qe_dependency`
- Ejemplo práctico completo
- Manejo de diferentes backends
- Ventajas del diseño
- Anti-patrones comunes

**Para quién:** Desarrolladores que quieren dominar completamente el sistema de tipado.

---

#### 3. [typing-quick-reference.md](./typing-quick-reference.md) - Referencia Rápida
Una referencia rápida con patrones comunes y checklists.

**Contiene:**
- Tipado por backend (Beanie, SQLAlchemy)
- Patrones comunes para problemas típicos
- Lo que NO hacer
- Checklist de tipado
- Referencias a documentos más detallados

**Para quién:** Desarrolladores que necesitan una respuesta rápida mientras codifican.

---

#### 4. [typing-architecture.md](./typing-architecture.md) - Arquitectura Detallada
Un análisis profundo de las decisiones arquitectónicas detrás del sistema de tipado.

**Contiene:**
- Visión general del problema
- Estructura de tipos por niveles
- Flujo de tipos a través del sistema
- Ventajas del diseño
- Decisiones de diseño explicadas
- Comparación con alternativas
- Por qué Protocols vs Clases Base

**Para quién:** Contribuidores y personas interesadas en la arquitectura interna.

---

#### 5. [../../TYPING_CHANGES.md](../../TYPING_CHANGES.md) - Historial de Cambios
Documento que detalla todos los cambios realizados al sistema de tipado.

**Contiene:**
- Resumen de cambios
- Cambio principal: `Engine[T, QueryResultType]`
- TypeVars agregados
- Archivos modificados
- Impacto en código de usuarios
- Ventajas del nuevo diseño
- Ejemplo de adición de nuevo backend
- Migration guide
- FAQ

**Para quién:** Usuarios existentes que necesitan actualizar su código.

---

#### 6. [../../examples/typing_advanced.py](../../examples/typing_advanced.py) - Ejemplo Avanzado
Código ejecutable que demuestra los patrones de tipado.

**Contiene:**
- Definición de modelos Pydantic/Beanie
- Creación de engines type-safe
- Creación de dependencias type-safe
- Funciones helper con tipado correcto
- Rutas FastAPI con tipos explícitos
- Patrones avanzados (paginación, transformación)
- Comentarios sobre múltiples backends

**Para quién:** Desarrolladores que aprenden mejor con código.

---

## Flujo de Lectura Recomendado

### Para Principiantes
1. Leer [TYPING_SOLUTION.md](../../TYPING_SOLUTION.md) (respuesta directa)
2. Revisar [../../examples/typing_advanced.py](../../examples/typing_advanced.py) (código ejecutable)
3. Consultar [typing-quick-reference.md](./typing-quick-reference.md) (referencia rápida)

### Para Desarrolladores Intermedios
1. Leer [typing-guide.md](./typing-guide.md) (completo)
2. Estudiar [typing-architecture.md](./typing-architecture.md) (arquitectura)
3. Implementar usando [../../examples/typing_advanced.py](../../examples/typing_advanced.py) como guía

### Para Contribuidores
1. Estudiar [typing-architecture.md](./typing-architecture.md) (decisiones de diseño)
2. Revisar [../../TYPING_CHANGES.md](../../TYPING_CHANGES.md) (qué cambió)
3. Consultar [typing-guide.md](./typing-guide.md) (conceptos)

---

## Los Dos TypeVars Clave

```python
T = TypeVar("T", covariant=True)
# Representa: El modelo Pydantic (Product, User, etc.)

QueryResultType = TypeVar("QueryResultType", covariant=True)
# Representa: Lo que devuelve el backend (BeanieQueryResult, SQLAlchemyQueryResult, etc.)
```

## El Protocolo Engine

```python
class Engine(Protocol[T, QueryResultType]):
    """
    T: El modelo Pydantic utilizado para validación.
    QueryResultType: El tipo específico del backend.
    """
    def build_query(self, ast: FilterAST) -> QueryResultType:
        """Construye una consulta específica del backend."""
        ...
    
    def execute_query(self, ast: FilterAST) -> QueryResultType:
        """Ejecuta la consulta."""
        ...
```

## Ejemplo Mínimo

```python
from fastapi_qengine.backends.beanie import BeanieQueryEngine
from fastapi_qengine.backends.beanie.engine import BeanieQueryResult
from fastapi_qengine import create_qe_dependency

# 1. Crear engine
engine = BeanieQueryEngine(Product)

# 2. Crear dependencia
qe_dep = create_qe_dependency(engine)

# 3. Usar en ruta
@app.get("/products")
async def get_products(
    query_result: BeanieQueryResult[Product] | None = Depends(qe_dep),
) -> list[Product]:
    if query_result is None:
        return await Product.find_all().to_list()
    
    query, projection_model, sort_spec = query_result
    return await query.to_list()
```

---

## Puntos Clave

✅ **Los tipos son documentación viva** - Comunican claramente qué devuelve cada backend

✅ **Type safety completo** - Los type checkers validan tu código

✅ **Extensible** - Agregar nuevos backends no requiere cambios en el core

✅ **Agnóstico del backend** - Tu lógica de negocio no depende del backend específico

❌ **No uses `Any`** - Pierdes todas las ventajas del sistema de tipado

❌ **No olvides el `| None`** - La dependencia retorna `None` si no hay filtro

❌ **No desempaque sin validar** - Siempre comprueba `if query_result is None`

---

## Contacto y Preguntas

Si tienes preguntas adicionales sobre tipado:
1. Consulta los documentos arriba (probablemente haya una respuesta)
2. Revisa [typing-quick-reference.md](./typing-quick-reference.md) para problemas comunes
3. Lee el código de ejemplo en [../../examples/typing_advanced.py](../../examples/typing_advanced.py)