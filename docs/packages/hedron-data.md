# hedron-data

DataTable, DataEditor, and data-source toolkit for Hedron.

**Package maturity:** Beta · **Train:** `0.63.x` (`v0.63.0` in-tree and on PyPI) · pin `>=0.63.0,<0.64`
**Flagship extra:** `hedron[data]` · **Import:** `hedron_data`  
**Capability:** Supported for DataTable / DataEditor (ABI `hedron-data-editor`) and
bounded `OptimisticMutation` when pinned — see [What’s ready](../guides/whats-ready.md)
and [DATA.md](../api/DATA.md).

## Install

```bash
pip install "hedron[data]>=0.63.0,<0.64"
# or
pip install "hedron-data>=0.63.0,<0.64"
```

Requires `hedron-core`. The package registers through the `hedron.plugins` entry
point on import/install.

### Optional extras

| Extra | Purpose |
|---|---|
| `dataframes` | pandas + polars + pyarrow (+ narwhals) |
| `pandas` / `polars` / `pyarrow` | Individual dataframe stacks |
| `sqlalchemy` / `sqlmodel` | ORM-backed sources |
| `dask` | Dask dataframe support |
| `snowflake` | Snowflake connector |
| `aggrid` / `spreadsheet` | Reserved feature gates (no heavy deps) |

```bash
pip install "hedron-data[dataframes]>=0.63.0,<0.64"
pip install "hedron-data[sqlalchemy]>=0.63.0,<0.64"
```

## When to use

- Paginated, sortable tables inside Hedron pages (FastAPI / Flask / Django)
- Editable grids with server-side save handlers and optional bounded optimistic cell edits
- Table↔chart cross-filter via `compose_chartlink_039` (Published 0.38 `hedron-chart` events)
- `DataSource` backends with explicit query and result contracts (in-memory, SQLAlchemy, Django QuerySet, …)

Prefer ordinary built-ins (`Table`, forms) for tiny static lists. Install this package
only when you need the grid toolkit.

## Quick start

```python
from hedron_data import Column, DataTable

table = DataTable(
    rows=({"id": "1", "name": "Ada"}, {"id": "2", "name": "Grace"}),
    columns=(Column("id", label="ID"), Column("name", label="Name")),
    caption="People",
    page_size=25,
)
```

Validated rows:

```python
from pydantic import BaseModel
from hedron_data import DataTable


class EmployeeRow(BaseModel):
    name: str
    team: str


table = DataTable(
    [{"name": "Ada", "team": "Platform"}],
    row_model=EmployeeRow,
    caption="Employees",
)
```

## Surfaces

| Surface | Role |
|---|---|
| `DataTable` | Read-only accessible grid (Tabulator-backed) |
| `DataEditor` | Editable grid; `on_save` is server-only configuration |
| `Column` / `columns_from_model` | Column catalog helpers |
| `InMemoryDataSource` / `SQLAlchemyDataSource` / … | Bounded query backends |
| `DjangoQuerySetDataSource` | Deny-by-default QuerySet allowlists |
| `DataQuery` / `DataPage` / `DataChanges` | Paging and mutation contracts |
| Grid events | `validate_grid_event` / `authorized_grid_event` |

Django QuerySet sources: supply an already-authorized base QuerySet; omitted
sort/filter allowlists deny client refinements. Query budgets raise
`QueryBudgetExceeded`.

## Errors and failure modes

| Condition | Behavior |
|---|---|
| Package not installed | `ImportError` for `DataTable` / `hedron_data` |
| Missing sort/filter allowlist on QuerySet source | Client refinements denied |
| Query budget exceeded | Fail closed with `QueryBudgetExceeded` |
| `on_save` in serializable props | Not part of the props contract — configure server-side only |

## Related docs

- Guide: [Data applications](../guides/data-apps.md)
- API: [Data](../api/DATA.md) · [Data sources](../api/DATA_SOURCE.md)
- Components: [DataTable](../components/data-table.md) · [DataEditor](../components/data-editor.md)
- Adapters: [Framework adapters](../api/ADAPTERS.md)

## Links

- [PyPI](https://pypi.org/project/hedron-data/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-data/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-data)
