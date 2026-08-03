# Data-source protocols

**Status:** Proposed

```python
class UsersSource(DataEditorSource[UserRow]):
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
- `DataEditorSource[T]`: fetch and apply protocol.
- `VisualizationSource[T]`: load protocol for charts and maps.

Protocols support synchronous and asynchronous implementations without changing component construction. Application adapters own transactions, tenant scope, authorization, and domain validation. Hedron owns request validation, size bounds, cancellation, diagnostics, and serialization.

No source is automatically inferred from an ORM model in the MVP because such inference could accidentally expose fields or mutation behavior.

