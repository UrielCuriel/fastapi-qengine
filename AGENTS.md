# Repository Guidelines

## Project Structure & Module Organization
- `fastapi_qengine/`: Library code
  - `core/`: parsing, normalization, AST, compiler base
  - `operators/`: comparison, logical, custom operators
  - `backends/`: backend compilers (e.g., `beanie.py`)
  - `dependency.py`, `openapi_schema.py`: FastAPI integration helpers
- `tests/`: pytest suite (`test_basic.py`, `test_validation.py`, `test_operators.py`)
- `examples/`: runnable usage samples (see `example.py`)
- `docs/` + `pydoc-markdown.yml`: API docs configuration

## Build, Test, and Development Commands
- Install dev deps: `uv pip install -e ".[dev]"` (or `pip install -e ".[dev]"`)
- Run tests: `uv run pytest`
- Coverage (HTML at `htmlcov/index.html`): `uv run pytest --cov=fastapi_qengine --cov-report=html`
- Lint: `ruff check fastapi_qengine/`
- Format: `ruff format fastapi_qengine/`
- Example app (requires MongoDB): `uv run python example.py`

## Coding Style & Naming Conventions
- Python 3.9+ (3.12 recommended). Use type hints and 4-space indentation.
- Modules and files: `snake_case.py`; classes: `PascalCase`; functions/vars: `snake_case`.
- Keep public APIs minimal; prefer explicit exports in `__init__.py`.
- Use `ruff` for linting/formatting; match existing import order and docstring tone.

## Testing Guidelines
- Framework: `pytest` with `pytest-asyncio` and `httpx` for HTTP tests.
- Place tests in `tests/`, name files `test_*.py`; functions `test_*`.
- Prefer focused unit tests in `core/` and operator behavior; add integration tests for backends.
- Aim to keep or improve coverage; add tests for new paths and errors.

## Commit & Pull Request Guidelines
- Commits: imperative mood, concise scope, e.g., `Add Beanie $in operator handling`.
- PRs: include summary, rationale, linked issues, and notes on breaking changes.
- Required: passing CI, updated/added tests, no coverage regressions, and docs/examples updated if APIs change.

## Security & Configuration Tips
- No secrets in code or tests. Use environment variables for local credentials.
- Example app depends on MongoDB for Beanie; library code should not require services at import time.
