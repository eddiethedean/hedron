# Migrate a Streamlit app

Streamlit and Hedron can both turn Python data into an interactive dashboard, but they
use different execution models. Streamlit reruns the application script when a widget
changes. Hedron handles an HTTP request, validates its inputs with FastAPI, and returns
typed server-rendered components. Migrate the user workflow first; do not translate each
call in isolation.

This guide rewrites a small sales dashboard with filters, metrics, and a table. On Hedron
**0.25**, published chart wheels are unavailable — use `Metric` + `DataTable` (or `Table`)
from PyPI, then add charts from the workspace when you need them.

## The Streamlit version

A typical single-file Streamlit app might look like this:

```python title="streamlit_app.py"
import pandas as pd
import streamlit as st


@st.cache_data
def load_sales() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"month": "Jan", "region": "North", "revenue": 3200, "orders": 32},
            {"month": "Feb", "region": "North", "revenue": 4100, "orders": 38},
            {"month": "Mar", "region": "North", "revenue": 4600, "orders": 41},
            {"month": "Jan", "region": "South", "revenue": 2800, "orders": 29},
            {"month": "Feb", "region": "South", "revenue": 3600, "orders": 34},
            {"month": "Mar", "region": "South", "revenue": 4300, "orders": 39},
        ]
    )


sales = load_sales()

st.title("Sales dashboard")
region = st.sidebar.selectbox("Region", ["All", "North", "South"])
minimum = st.sidebar.slider("Minimum revenue", 0, 5000, 0, step=500)

filtered = sales[
    ((sales["region"] == region) | (region == "All"))
    & (sales["revenue"] >= minimum)
]

revenue, orders = st.columns(2)
revenue.metric("Revenue", f"${filtered['revenue'].sum():,}")
orders.metric("Orders", int(filtered["orders"].sum()))

st.line_chart(filtered, x="month", y="revenue")
st.dataframe(filtered, width="stretch")
```

The controls are declarations embedded in top-to-bottom execution. When either control
changes, Streamlit reruns the file and reconstructs the page.

## Rewrite it in Hedron

Install Hedron with the data extra, plus an ASGI server:

```bash
uv add "hedron[data]>=0.25.0,<0.26" "uvicorn[standard]"
```

!!! danger "Do not install charts from PyPI with Hedron 0.25"

    Do not install the charts extra or `hedron-charts` from PyPI — those releases require
    older `hedron-core` and will break a 0.25 environment. See
    [Compatibility](../COMPATIBILITY.md#current-025-packaging-limitation-charts-and-sample-kit).
    For a PyPI-installable dashboard, use metrics and tables (below). Workspace clones can
    follow the [workspace-only charts](#workspace-only-charts-on-025) section.

Create `app.py`:

```python title="app.py"
from typing import Annotated, Literal

from fastapi import Query
from hedron import (
    Form,
    FormField,
    Grid,
    Heading,
    Hedron,
    Metric,
    Model,
    Page,
    Select,
    Sidebar,
    Stack,
    SubmitButton,
    Table,
    cache_data,
    html,
)
from hedron_data import DataTable

Region = Literal["All", "North", "South"]


class SalesRow(Model):
    month: str
    region: str
    revenue: int
    orders: int


@cache_data(ttl=300, scope="public")
def load_sales() -> list[SalesRow]:
    return [
        SalesRow(month="Jan", region="North", revenue=3200, orders=32),
        SalesRow(month="Feb", region="North", revenue=4100, orders=38),
        SalesRow(month="Mar", region="North", revenue=4600, orders=41),
        SalesRow(month="Jan", region="South", revenue=2800, orders=29),
        SalesRow(month="Feb", region="South", revenue=3600, orders=34),
        SalesRow(month="Mar", region="South", revenue=4300, orders=39),
    ]


app = Hedron(
    title="Sales dashboard",
    security="standard",
    session_secret="dev-only-change-me",
)


@app.page("/")
def dashboard(
    region: Annotated[Region, Query()] = "All",
    minimum: Annotated[int, Query(ge=0, le=5000)] = 0,
) -> Page:
    filtered = [
        row
        for row in load_sales()
        if (region == "All" or row.region == region) and row.revenue >= minimum
    ]
    by_month: dict[str, int] = {}
    for row in filtered:
        by_month[row.month] = by_month.get(row.month, 0) + row.revenue
    month_rows = [[month, f"${total:,}"] for month, total in by_month.items()]

    filters = Sidebar(
        Heading("Filters", level=2),
        Form(
            FormField(
                name="region",
                label="Region",
                control=Select(
                    "region",
                    [("All", "All"), ("North", "North"), ("South", "South")],
                    value=region,
                ),
            ),
            FormField(
                name="minimum",
                label="Minimum revenue",
                control=html.input(
                    type="range",
                    name="minimum",
                    min="0",
                    max="5000",
                    step="500",
                    value=str(minimum),
                ),
            ),
            SubmitButton("Apply filters"),
            action="/",
            method="get",
        ),
        label="Dashboard filters",
    )

    content = Stack(
        Heading("Sales dashboard", level=1),
        Grid(
            Metric("Revenue", f"${sum(row.revenue for row in filtered):,}"),
            Metric("Orders", sum(row.orders for row in filtered)),
            columns=2,
        ),
        Heading("Revenue by month", level=2),
        Table(
            ["Month", "Revenue"],
            month_rows or [["—", "No rows"]],
            caption="Monthly revenue for the selected region and minimum.",
        ),
        DataTable(
            filtered,
            row_model=SalesRow,
            caption="Filtered sales",
            empty_message="No sales match these filters.",
        ),
    )

    return Page(Grid(filters, content, columns=2), title="Sales dashboard")
```

Run it:

```bash
uv run uvicorn app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Applying the form issues a
`GET /?region=...&minimum=...` request. The URL is bookmarkable, FastAPI validates the
query parameters, and the route returns a new component tree. A production application
should load `session_secret` from its environment rather than using the development
literal shown above.

### Workspace-only charts on 0.25

When you develop against this monorepo (or an editable checkout that includes
`packages/hedron-charts`), you can restore a `LineChart` in place of the month `Table`:

```python
# workspace-only — requires packages/hedron-charts on PYTHONPATH / uv workspace
from hedron_charts import LineChart

LineChart(
    [row.model_dump() for row in filtered],
    x="month",
    y="revenue",
    title="Revenue by month",
    description="Monthly revenue for the selected region and minimum.",
)
```

Do not `pip install hedron-charts` from PyPI into a 0.25 app. Details:
[Charts and HTMX](charts-and-htmx.md).

## How the concepts map

| Streamlit | Hedron | Migration note |
|---|---|---|
| `st.title`, `st.write` | `Heading`, `Text`, `Markdown`, or `Auto` | Return components from a page route instead of emitting them as side effects. |
| `st.sidebar` | `Sidebar` | A sidebar is an explicit child in the page layout. |
| `st.selectbox`, `st.slider` | `Select` or native controls inside `Form` | Bind submitted values to typed FastAPI query or form parameters. |
| `st.columns` | `Grid` or `Inline` | Compose child components explicitly. |
| `st.metric` | `Metric` | Pass the label, formatted value, and optional delta. |
| `st.dataframe` | `DataTable` | Declare a `Model` when stable column types matter. Use `DataEditor` for edits. |
| `st.line_chart` | `Table` / `Metric` on PyPI 0.25; `LineChart` workspace-only | Source-only charts until a compatible wheel is published; provide a title and accessible description when charts return. |
| `st.plotly_chart` | `PlotlyChart` (workspace-only on 0.25) | Hedron compiles the supported figure through its chart adapter. |
| `st.cache_data` | `cache_data` | Choose a TTL and a cache scope; include user or tenant dimensions for private data. |
| `st.session_state` | Query parameters, your database, or `SessionState` | Prefer addressable URL state for filters and durable application storage for domain data. |
| `st.file_uploader` | `FileUpload` | Process uploads in an explicit server action with size and content policies. |

## Replace reruns with requests and actions

The largest migration decision is where code runs:

- Put initial page composition and safe filters in `@app.page` routes.
- Use ordinary FastAPI dependencies for authentication, database sessions, and request
  validation.
- Model mutations as explicit `POST`, `PUT`, `PATCH`, or `DELETE` actions. Enforce
  authorization and CSRF at that boundary; do not translate `if st.button(...):` into a
  page-render side effect.
- Return targeted fragments and add HTMX when only part of the page should update. Start
  with the full-page GET form above, then follow [HTMX interactions](htmx-interactions.md).
- Keep long-running work outside the render path and expose its status through jobs or
  polling rather than blocking a page request.

This separation makes filters addressable, mutations auditable, and components testable
without a browser. Continue with [Test your UI](testing.md), [Security](security.md), and
[Data applications](data-apps.md).
