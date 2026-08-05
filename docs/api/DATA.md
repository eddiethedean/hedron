---
status: shipped
---

# `DataTable` and `DataEditor`

!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).

**Status:** Accepted · **Shipped** (install `hedron[data]`)

```bash
pip install "hedron[data]"
```

```python
from hedron_data import Column, DataTable

DataTable(
    rows=({"id": "1", "name": "Ada"},),
    columns=(Column("id", label="ID"), Column("name", label="Name")),
    caption="People",
)
```

## `DataTable`

Read-only accessible table with paging metadata and optional CSV download.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `rows` | sequence / mappings | `None` | In-memory rows when `page` is omitted |
| `row_model` | `type[Model] \| None` | `None` | Optional typed row model for column inference |
| `columns` | sequence of `Column` | `None` | Explicit columns |
| `page` | `DataPage \| None` | `None` | Pre-paged data from a source |
| `query` | `DataQuery \| None` | `None` | Sort/filter/page query metadata |
| `caption` | `str \| None` | `None` | Table caption |
| `empty_message` | `str` | `"No rows"` | Empty state copy |
| `page_size` | `int` | `25` | Default page size |
| `allow_download` | `bool` | `False` | Enable CSV helper when true |

## `DataEditor`

Editable grid hosted by a Web Component. `on_save` is **server-only factory
configuration** — never part of the serializable props contract. Prefer an explicit
`DataEditorSource` for large data.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `rows` | sequence / mappings | `None` | Initial rows when `page` / `source` omitted |
| `key` | `str` | `"editor"` | Stable browser editor identity |
| `row_model` | `type[Model] \| None` | `None` | Typed row model |
| `columns` | sequence of `Column` | `None` | Explicit columns |
| `key_field` | `str` | `"id"` | Stable row identity field |
| `on_save` | callable \| `None` | `None` | Server-only save handler `(DataChanges) -> DataSaveResult` |
| `source` | `DataEditorSource` \| async variant | `None` | Preferred for large data |
| `page` | `DataPage \| None` | `None` | Pre-paged data |
| `save_mode` | `"batch"` \| `"row"` \| `"cell"` | `"batch"` | Client save granularity |
| `page_size` | `int` | `25` | Page size |
| `caption` | `str \| None` | `None` | Caption |
| `save_endpoint` | `str \| None` | `None` | Explicit save URL when not inferred |
| `allow_deletes` | `bool` | `True` | Whether deletes are accepted |

| Concept | Type | Description |
|---|---|---|
| `DataChanges[Row]` | model | Updates, inserts, deletes, optional versions |
| `DataSaveResult[Row]` | model | Success, normalized values, field errors, concurrency conflicts |
| Writable fields | server policy | Visible fields are not automatically writable; validate on every save |

## Errors

| Situation | Behavior |
|---|---|
| Missing `hedron-data` | Import error — install `hedron[data]` |
| Unauthorized / invalid save | Application / `DataSaveResult` field errors |
| Oversized client payload | Bounded serialization failure / diagnostic |

## See also

- [Data sources](DATA_SOURCE.md) — protocols, `InMemoryDataSource`, paging
- [Data applications guide](../guides/data-apps.md) — SQLAlchemy end-to-end
- [DataTable component](../components/data-table.md) · [DataEditor](../components/data-editor.md) · [Field](FIELD.md)
