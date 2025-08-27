# Desarrollo y Testing

## Configuración del Entorno de Desarrollo

### Requisitos
- Python 3.12+
- uv (recomendado) o pip

### Instalación para Desarrollo

```bash
# Clonar el repositorio
git clone https://github.com/tuusuario/fastapi-qengine.git
cd fastapi-qengine

# Instalar dependencias de desarrollo
uv pip install -e ".[dev]"
# o con pip:
# pip install -e ".[dev]"
```

## Testing con pytest

### Ejecutar Todos los Tests

```bash
# Con uv (recomendado)
uv run pytest

# Con pytest directamente (si está en PATH)
pytest

# Con cobertura
uv run pytest --cov=fastapi_qengine --cov-report=html
```

### Ejecutar Tests Específicos

```bash
# Tests de un módulo específico
uv run pytest tests/test_basic.py

# Tests de una clase específica
uv run pytest tests/test_basic.py::TestFilterParser

# Un test específico
uv run pytest tests/test_basic.py::TestFilterParser::test_parse_json_string

# Tests con palabra clave
uv run pytest -k "parser"

# Tests que fallan
uv run pytest --lf
```

### Opciones de Pytest Útiles

```bash
# Verbose output
uv run pytest -v

# Traceback corto
uv run pytest --tb=short

# Mostrar print statements
uv run pytest -s

# Ejecutar en paralelo (requiere pytest-xdist)
uv run pytest -n auto

# Perfil de tiempo
uv run pytest --durations=10
```

### Configuración de pytest

La configuración está en `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--verbose",
    "--tb=short",
    "--strict-markers",
    "--disable-warnings",
    "--cov=fastapi_qengine",
    "--cov-report=term-missing",
    "--cov-report=html",
]
asyncio_mode = "auto"
```

## Estructura de Tests

```
tests/
├── __init__.py
├── conftest.py              # Configuración y fixtures compartidas
├── test_basic.py           # Tests básicos del pipeline
├── test_validation.py      # Tests de validación y seguridad
└── test_operators.py       # Tests de operadores
```

### Fixtures Disponibles

- `sample_filter_data`: Datos de filtros de ejemplo
- `sample_nested_params`: Parámetros anidados de ejemplo  
- `sample_json_strings`: Strings JSON de ejemplo
- `mock_beanie_model`: Mock de modelo Beanie para testing

## Coverage

### Generar Reporte de Cobertura

```bash
# HTML report (recomendado para desarrollo)
uv run pytest --cov=fastapi_qengine --cov-report=html

# Terminal report
uv run pytest --cov=fastapi_qengine --cov-report=term-missing

# XML report (para CI/CD)
uv run pytest --cov=fastapi_qengine --cov-report=xml
```

El reporte HTML se genera en `htmlcov/index.html`.

### Configuración de Coverage

```toml
[tool.coverage.run]
source = ["fastapi_qengine"]
omit = [
    "tests/*",
    "example.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
```

## Testing de la API FastAPI

### Test Manual con el Ejemplo

```bash
# Ejecutar el ejemplo (requiere MongoDB)
uv run python example.py

# En otra terminal, probar endpoints
curl "http://localhost:8000/products"
curl "http://localhost:8000/products?filter[where][category]=electronics"
```

### Tests de Integración

Para tests de integración con FastAPI:

```python
import pytest
from fastapi.testclient import TestClient
from example import app

@pytest.fixture
def client():
    return TestClient(app)

def test_products_endpoint(client):
    response = client.get("/products")
    assert response.status_code == 200
```

## Herramientas de Desarrollo

### Pre-commit Hooks (Opcional)

```bash
# Instalar pre-commit
pip install pre-commit

# Configurar hooks
pre-commit install
```

### Linting y Formateo

```bash
# Con ruff (si está instalado)
ruff check fastapi_qengine/
ruff format fastapi_qengine/

# Con black y isort
black fastapi_qengine/
isort fastapi_qengine/
```

## Debugging

### Debugging Tests

```bash
# Con pdb
uv run pytest --pdb

# Con ipdb (más avanzado)
pip install ipdb
uv run pytest --pdb-trace

# Debugging específico
import pdb; pdb.set_trace()  # En el código
```

### Logging en Tests

```python
import logging
logging.basicConfig(level=logging.DEBUG)

def test_with_logging():
    logger = logging.getLogger(__name__)
    logger.debug("Debug info")
```

## CI/CD

### GitHub Actions

Ejemplo de workflow para GitHub Actions:

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.12]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install uv
        uv pip install -e ".[test]"
    
    - name: Run tests
      run: uv run pytest --cov=fastapi_qengine --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Contribuciones

### Agregar Nuevos Tests

1. Crear el archivo de test en `tests/`
2. Usar fixtures existentes cuando sea posible
3. Seguir las convenciones de nomenclatura (`test_*.py`)
4. Documentar el propósito del test

### Ejecutar Tests Antes de Commit

```bash
# Comando completo recomendado
uv run pytest -v --cov=fastapi_qengine --cov-report=term-missing
```

Esto asegura que:
- Todos los tests pasen
- La cobertura se mantenga alta
- No hay regresiones

### Métricas de Calidad

Objetivos:
- **Cobertura de tests**: > 80%
- **Tests passing**: 100%
- **Performance**: Tests completos en < 30s
