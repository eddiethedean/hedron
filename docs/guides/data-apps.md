# Data applications

Render common Python objects with core `Auto`, then install the data extra for
tabular `DataTable` / `DataEditor`.

## Auto (core — no extra)

```python
from hedron import Auto, Hedron, Page, Stack

app = Hedron(title="Data", security="standard", session_secret="replace-me")


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            Auto({"name": "Ada", "role": "admin"}),
            Auto([1, 2, 3]),
        ),
        title="Auto",
    )
```

`Auto` picks an inspectable renderer; override or register renderers when you need
control ([Auto API](../api/AUTO.md)).

## DataTable (requires `hedron[data]`)

```bash
uv add "hedron[data]"
# optional backends
uv add "hedron-data[pandas]"
```

```python
from hedron import Hedron, Page
from hedron_data import Column, DataTable

app = Hedron(title="Table", security="standard", session_secret="replace-in-production")


@app.page("/")
def home() -> Page:
    return Page(
        DataTable(
            rows=(
                {"id": "1", "name": "Ada"},
                {"id": "2", "name": "Grace"},
            ),
            columns=(Column("id", label="ID"), Column("name", label="Name")),
        ),
        title="People",
    )
```

For editable grids, CSRF-backed saves, and query protocols, see
[Data](../api/DATA.md), [Data sources](../api/DATA_SOURCE.md), and the
[reference app](../examples/reference-app.md).

## Charts

Install `hedron[charts]` and follow [Charts and HTMX](charts-and-htmx.md).
