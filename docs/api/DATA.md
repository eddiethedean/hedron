---
status: shipped
---

# `DataTable` and `DataEditor`

!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).

**Status:** Accepted · **Shipped** (install `hedron[data]`)

```bash
pip install "hedron[data]>=0.46.0,<0.47"
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

Editable grid hosted by the public **`hedron-data-editor`** custom element
(`TAG_NAME = "hedron-data-editor"`). Markup is ABI-shaped
(`<hedron-data-editor data-hedron-abi …>`) with the previous SSR table retained
inside as a progressive-enhancement fallback (`data-hedron-fallback` /
`aria-hidden` after boot). `on_save` is **server-only factory configuration** —
never part of the serializable props contract. Prefer an explicit
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

## `OptimisticMutation` (0.39)

Typed optimistic edit contract for **bounded DataEditor / collection cell edits**.
Import from `hedron_data`:

```python
from hedron_data import OptimisticMutation, OptimisticMutationState, assert_optimism_allowed
```

State machine: `canonical` → `proposed` → `submitted` → `confirmed` (with
`rejected` / `rolled_back` / `conflicted` / `refetched` branches). Every mutation
carries an idempotency key and optional base revision. Risk classes outside the
proven inventory (auth, payments, irreversible deletes, bulk admin, …) are
**deny-by-default** via `assert_optimism_allowed` / `DENY_BY_DEFAULT_RISKS`.

Server-confirmed remains the default truth; the browser may paint proposed state
only for allowlisted collection edits.

## Chartlink (0.39)

Compose Published 0.38 `hedron-chart` events with DataTable/DataEditor selection
without a parallel chart renderer:

```python
from hedron_core.cross_filter import compose_chartlink_039
```

`compose_chartlink_039` binds chart event kinds from the Published chart contract
to grid selection / filter state. Keep vendor chart adapters Experimental and
out of the default Supported path.

## Errors

| Situation | Behavior |
|---|---|
| Missing `hedron-data` | Import error — install `hedron[data]` |
| Unauthorized / invalid save | Application / `DataSaveResult` field errors |
| Oversized client payload | Bounded serialization failure / diagnostic |
| Disallowed optimistic risk | Fail closed (`assert_optimism_allowed`) |

## See also

- [Data sources](DATA_SOURCE.md) — protocols, `InMemoryDataSource`, paging
- [Data applications guide](../guides/data-apps.md) — SQLAlchemy end-to-end
- [DataTable component](../components/data-table.md) · [DataEditor](../components/data-editor.md) · [Field](FIELD.md)
- [What’s new in 0.39](../guides/whats-new-0.39.md)
