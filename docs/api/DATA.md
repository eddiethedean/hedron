---
status: shipped
---

# `DataTable` and `DataEditor`

!!! note "Stability (0.8 compatibility baseline)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).

**Status:** Accepted · **Shipped** (install `hedron[data]`)

```bash
pip install "hedron[data]"
```

```python
from hedron_data import Column, DataTable, InMemoryDataSource

source = InMemoryDataSource(
    rows=({"id": "1", "name": "Ada"},),
    columns=(Column("id", label="ID"), Column("name", label="Name")),
)
DataTable(source=source)
```

`on_save` on `DataEditor` is server-only factory configuration. It is never part of the
serializable component props contract. Prefer an explicit `DataEditorSource` for large data.

## `DataTable`

Presents normalized tabular data with declared columns, accessible headers, bounded
pagination, sorting, filtering, empty state, and download policy. It does not make data
editable.

## `DataEditor`

Adds a Web Component grid and typed save resources. `DataChanges[Row]` carries updates,
inserts, deletes, and optional versions. `DataSaveResult[Row]` reports success,
normalized values, validation errors, and optimistic-concurrency conflicts.

Visible fields are not automatically writable. The server validates read-only and
authorization rules on every change.

## Errors

| Situation | Behavior |
|---|---|
| Missing `hedron-data` | Import error — install `hedron[data]` |
| Unauthorized / invalid save | Application/`DataSaveResult` field errors |
| Oversized client payload | Bounded serialization failure / diagnostic |

## See also

- [Data apps guide](../guides/data-apps.md) · [Data sources](DATA_SOURCE.md) · [Field](FIELD.md)
