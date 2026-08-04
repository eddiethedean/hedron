---
status: shipped
---

# `DataTable` and `DataEditor`


!!! note "Stability (0.8 compatibility baseline)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Accepted

```python
DataTable(rows, row_model=EmployeeRow)

DataEditor(
    employees,
    key="employees",
    row_model=EmployeeRow,
    on_save=save_employees,
)
```

`on_save` is server-only factory configuration that creates a typed action binding. It is never part of the serializable component props contract. Reusable and large-data editors should prefer an explicit `DataEditorSource`.

## `DataTable`

Presents normalized tabular data with declared columns, accessible headers, bounded pagination, sorting, filtering, empty state, and download policy. It does not make data editable.

## `DataEditor`

Adds a Web Component grid and typed save resources. Column editors derive from row-model metadata and explicit column objects. Manual batch save is the default; row and cell commit modes share the same change contract.

`DataChanges[Row]` contains updated cells, inserted rows, deleted stable keys, and optional dataset or row versions. `DataSaveResult[Row]` reports success, normalized values, row/field validation errors, and optimistic-concurrency conflicts.

Visible fields are not automatically writable. The server validates read-only and authorization rules on every change. Large data uses a `DataEditorSource`; full client serialization is bounded.

Backend-specific options require an adapter namespace or escape hatch and cannot undermine security, accessibility, or portability guarantees.
