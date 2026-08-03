# Changelog

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
