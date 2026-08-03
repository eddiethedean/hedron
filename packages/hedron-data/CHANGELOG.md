# Changelog

## [0.6.0] - 2026-08-03

- Async `VisualizationSource` protocol and viz row/payload defaults.
- `SQLAlchemyDataSource` adapter (`hedron-data[sqlalchemy]` / `[sqlmodel]`).
- AG Grid Community host shim and `ensure_aggrid_assets()` (`hedron-data[aggrid]`).
- Bounded SQLAlchemy paging: `OFFSET`/`LIMIT` applied in SQL (not collect-all-then-slice).

## [0.5.0] - 2026-08-03

- Initial `hedron-data` package: data-source protocols, `DataTable`, `DataEditor`,
  in-memory paged sources (sync + async), optional Narwhals dataframe normalization, and
  Tabulator-shaped browser adapter assets.
- Async sources require explicit `page=` at construction; sync `apply_changes` raises for
  awaitable `apply` and `apply_changes_async` awaits correctly.
- Writable-field policy rejects forged read-only/hidden fields, unauthorized deletes, and
  non-mapping inserts.
- DataEditor host: undo DOM restore, insert/delete, save modes, conflict actions, choices
  and boolean editors, escaped selectors; CSS fingerprinted via plugin assets.

[0.5.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.5.0

[0.6.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.6.0
