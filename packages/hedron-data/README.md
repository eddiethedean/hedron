# hedron-data

[![PyPI](https://img.shields.io/pypi/v/hedron-data.svg)](https://pypi.org/project/hedron-data/)
[![Python](https://img.shields.io/pypi/pyversions/hedron-data.svg)](https://pypi.org/project/hedron-data/)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

DataTable, DataEditor, and data-source toolkit for Hedron.

Typed data-source protocols, optional dataframe normalization, and a
Tabulator-backed grid Web Component — registered through the public Hedron
plugin contract. Install as `hedron-data` or via the flagship extra `hedron[data]`.

**Package maturity:** Beta · **Train:** `0.54.x` (in-tree tip `v0.54.0`) · pin `>=0.54.0,<0.55` (PyPI still `>=0.52.0,<0.53` while deferred)

## Install

```bash
pip install "hedron-data>=0.52.0,<0.53"
# or
uv add "hedron-data>=0.52.0,<0.53"
# via flagship:
pip install "hedron[data]>=0.52.0,<0.53"
```

Requires Python 3.11–3.14 and `hedron-core`.

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
pip install "hedron-data[dataframes]>=0.52.0,<0.53"
pip install "hedron-data[sqlalchemy]>=0.52.0,<0.53"
```

## Quick start

```python
from hedron_data import DataTable

rows = [
    {"name": "Ada", "team": "Platform"},
    {"name": "Grace", "team": "Compiler"},
]
table = DataTable(rows, caption="Employees", page_size=25)
```

Use inside a Hedron `Page` (FastAPI / Flask / Django). Prefer a typed
`row_model` when you want validated columns:

```python
from pydantic import BaseModel
from hedron_data import DataTable


class EmployeeRow(BaseModel):
    name: str
    team: str


table = DataTable(rows, row_model=EmployeeRow, caption="Employees")
```

## What this package includes

- `DataTable` — paginated, sortable grid with HTMX-friendly refresh
- `DataEditor` — editable grid workflows
- Typed `DataSource` protocols and dataframe normalization helpers
- Tabulator-backed Web Component assets (plugin-registered)

## Links

- [Package docs](https://hedron.readthedocs.io/en/latest/packages/hedron-data/)
- [Data apps guide](https://hedron.readthedocs.io/en/latest/guides/data-apps/)
- [DataTable](https://hedron.readthedocs.io/en/latest/components/data-table/) ·
  [DataEditor](https://hedron.readthedocs.io/en/latest/components/data-editor/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-data/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-data)
- [Issues](https://github.com/eddiethedean/hedron/issues)
- [`hedron-core`](https://pypi.org/project/hedron-core/) ·
  [`hedron`](https://pypi.org/project/hedron/)

## License

MIT. See the [repository license](https://github.com/eddiethedean/hedron/blob/main/LICENSE).
