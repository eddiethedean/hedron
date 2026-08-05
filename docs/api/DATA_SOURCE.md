---
status: shipped
---

# Data-source protocols


!!! note "Stability (0.11 train)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Accepted

```python
class UsersSource(DataEditorSource[UserRow]):
    def fetch(self, query: DataQuery) -> DataPage[UserRow]: ...
    def apply(self, changes: DataChanges[UserRow]) -> DataSaveResult[UserRow]: ...


class AsyncUsersSource(AsyncDataEditorSource[UserRow]):
    async def fetch(self, query: DataQuery) -> DataPage[UserRow]: ...
    async def apply(
        self, changes: DataChanges[UserRow]
    ) -> DataSaveResult[UserRow]: ...
```

## Types

- `DataQuery`: bounded page/cursor, allowlisted sort and filter expressions, projection, search, and locale.
- `DataPage[T]`: rows, schema, continuation/count metadata, and optional version.
- `DataChanges[T]`: inserts, updates, deletes, and submitted versions.
- `DataSaveResult[T]`: accepted changes, normalized values, errors, conflicts, and new versions.
- `DataEditorSource[T]`: sync fetch and apply protocol.
- `AsyncDataEditorSource[T]`: async fetch and apply protocol.
- `VisualizationSource[T]`: async/sync load protocol for charts (shipped in 0.6 with
  `hedron-charts`).
- `InMemoryDataSource`: concrete sync source for tests and small apps (re-exported from
  `hedron` when `hedron[data]` is installed). See [data applications](../guides/data-apps.md).
- `SQLAlchemyDataSource`: `hedron_data.sqlalchemy_source` — app-owned sessions; paging via
  SQL `OFFSET`/`LIMIT`. Sort/filter/search on `DataQuery` not yet translated (`HED-DATA-0012`).

## Sync vs async construction

Protocols support synchronous and asynchronous implementations. `DataEditor` construction
is synchronous:

- Sync sources may be passed as `source=`; Hedron calls `fetch` during construction.
- Async sources must not be awaited during construction. Await `source.fetch(...)` in the
  route and pass `page=...` (optionally still attach `source=` for `apply_changes_async`).
- Sync `DataEditor.apply_changes` raises if `source.apply` returns an awaitable; use
  `await editor.apply_changes_async(...)` instead.

Application adapters own transactions, tenant scope, authorization, and domain validation.
Hedron owns request validation, size bounds, cancellation, diagnostics, and serialization.

No source is automatically inferred from an ORM model in the MVP because such inference could accidentally expose fields or mutation behavior.
