---
status: implemented
---

# Edron 0.3 data workspace contract

Edron 0.3 adds explicit, request-bounded data workspace vocabulary over native
`hedron-data`. Hedron remains the data renderer, source protocol, edit-policy filter,
concurrency, fallback, and serialization authority. Edron does not own rows, sessions,
transactions, authorization state, persistence, or audit storage.

## Source and workspace

`DataSource` wraps one explicit native source exposing `fetch(DataQuery)` and
`apply(DataChanges)`. `DataSource.in_memory()` is intended for bounded application data,
tests, and examples. `DataSource.dataframe()` adapts installed pandas, Polars, PyArrow, or
Narwhals values through native normalization. `DataSource.sqlalchemy()` delegates to the
native SQLAlchemy adapter and therefore keeps session and transaction ownership in the
application.

```python
import edron as ed

columns = (
    ed.Column("id", read_only=True, sortable=True),
    ed.Column("name", writable=True, filterable=True),
)
source = ed.DataSource.in_memory(
    [{"id": "1", "name": "Ada"}],
    columns=columns,
    writable_fields=("name",),
    sort_fields=("id",),
    filter_fields=("name",),
    projection_fields=("id", "name"),
)
workspace = ed.DataWorkspace(
    "people",
    source=source,
    columns=columns,
    edit=ed.EditPolicy(
        writable_fields=frozenset({"name"}),
        authorize=lambda intent, principal: principal is not None,
        audit=record_audit_event,
    ),
)
app.data_workspace(workspace)  # registers the CSRF-protected native JSON save action
```

Columns, row identity, sort/filter/projection fields, page size, and writable fields are
explicit. Page limits are capped by the workspace and by Hedron's hard limit. Secret fields
cannot be projection fields. Async sources must be fetched and persisted by an explicit async
application action; synchronous component construction never runs an event loop.

## Reading, paging, selection, and export

`PageRequest` carries offset, limit, allowlisted sort/filter/search, and projection inputs.
`DataWorkspace.page()` returns a `WorkspacePage` retaining the native page and safe metadata.
`DataSelection` is limited to 500 unique row identities and may only name rows in the current
authorized page. `export_csv()` exports that page or its selection only; it does not collect the
whole source, omits hidden/secret columns, and uses the native spreadsheet formula sanitizer.

Inside a page, `data_workspace()` reads ordinary query parameters through the workspace
allowlists. `data_editor()` is its explicit editable spelling:

```python
@app.page("/people", title="People")
class People(ed.Page):
    def render(self) -> None:
        page = self.data_editor(workspace)
```

Both methods lower to native `DataTable` or `DataEditor`. The editor retains its server-rendered
accessible table fallback. For complete list/detail/create/edit form routes,
`workspace.native_feature(...)` returns the owning native `DataWorkspace`, which can be passed to
`app.include(...)`; its create and edit routes are ordinary typed forms.

## Editing contract

`EditIntent` contains one or more typed `CellEdit` updates, insert mappings, or delete row keys,
with optional dataset/row revisions and a bounded reason. A request is limited to 500 operations.
`EditPolicy` is deny-by-default:

- no `authorize` hook means every edit is rejected;
- update fields must be in its explicit `writable_fields` and in native columns marked
  `writable=True`;
- inserts and deletes require separate opt-in;
- `validate` may return native `FieldError` values or bounded messages; and
- `audit` receives `AuditEvent` metadata after the native result, never cell values.

The native source returns `DataSaveResult`, including validation errors and revision conflicts.
Edron does not retry, overwrite, commit, roll back, or resolve conflicts. Applications needing an
audit record in the same transaction as persistence must implement both in their source adapter.

## Diagnostics and boundaries

`DataWorkspace.diagnostics()` reports adapter type, bounds, allowlists, editability, and whether
authorization/validation/audit hooks are explicit. It never fetches rows or emits values.

Edron 0.3 deliberately does not infer ORM managers, discover tables, own transactions, provide a
repository, install dataframe/SQLAlchemy dependencies at runtime, or turn buttons into implicit
mutations.
