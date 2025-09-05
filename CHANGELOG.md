# Changelog

## 0.4.0 - 2025-09-05

- Features: add flexible order parsing in `FilterNormalizer` and `ASTBuilder` supporting multiple formats:
  - String with keywords: `"field ASC"`, `"field DESC"`
  - Minus shorthand: `"-field"`
  - Comma-separated lists: `"field1 ASC, field2 DESC, -field3"`
  - Arrays of items: `["field1 ASC", "field2 DESC"]`
  - Also supported when provided via JSON strings and nested query params (e.g., `filter[order]`, `filter[order][0]`).
- Tests: add comprehensive coverage for the new order formats.
- Compatibility: no breaking changes to existing filter/ordering behavior.

## 0.2.0 - 2025-08-28

- Features: add response model factory to ease pagination integration; examples updated with pagination support.
- Architecture: introduce explicit backend engines (e.g., `BeanieQueryEngine`) and compiler utilities.
- Refactor: improve operator handling and validation; streamline core structure for readability.
- Docs: full docs refresh (Getting Started, Beanie and SQLAlchemy guides, examples); new reference sections.
- Tooling: compute package version via `importlib.metadata`; align project metadata in `pyproject.toml`.

Notes:
- For Beanie usage, instantiate an engine (`BeanieQueryEngine(Model)`) and pass it to `create_qe_dependency(...)`. See `examples/` and docs for the updated pattern.
