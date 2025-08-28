# Changelog

## 0.2.0 - 2025-08-28

- Features: add response model factory to ease pagination integration; examples updated with pagination support.
- Architecture: introduce explicit backend engines (e.g., `BeanieQueryEngine`) and compiler utilities.
- Refactor: improve operator handling and validation; streamline core structure for readability.
- Docs: full docs refresh (Getting Started, Beanie and SQLAlchemy guides, examples); new reference sections.
- Tooling: compute package version via `importlib.metadata`; align project metadata in `pyproject.toml`.

Notes:
- For Beanie usage, instantiate an engine (`BeanieQueryEngine(Model)`) and pass it to `create_qe_dependency(...)`. See `examples/` and docs for the updated pattern.

