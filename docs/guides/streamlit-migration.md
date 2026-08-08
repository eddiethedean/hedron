# Migrate a Streamlit app

Streamlit and Hedron can both turn Python data into an interactive dashboard, but they
use different execution models. Streamlit reruns the application script when a widget
changes. Hedron handles an HTTP request, validates its inputs with FastAPI, and returns
typed server-rendered components. Migrate the user workflow first; do not translate each
call in isolation.

This guide rewrites a small sales dashboard with filters, metrics, a chart, and a table.

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

Install Hedron with its data and chart packages, plus an ASGI server:

```bash
uv add "hedron[data]>=0.22.0,<0.23" "hedron[charts]>=0.1.0,<0.2" "uvicorn[standard]"
```

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
    cache_data,
    html,
)
from hedron_charts import LineChart
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
    chart_rows = [row.model_dump() for row in filtered]

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
        LineChart(
            chart_rows,
            x="month",
            y="revenue",
            title="Revenue by month",
            description="Monthly revenue for the selected region and minimum.",
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

## How the concepts map

| Streamlit | Hedron | Migration note |
|---|---|---|
| `st.title`, `st.write` | `Heading`, `Text`, `Markdown`, or `Auto` | Return components from a page route instead of emitting them as side effects. |
| `st.sidebar` | `Sidebar` | A sidebar is an explicit child in the page layout. |
| `st.selectbox`, `st.slider` | `Select` or native controls inside `Form` | Bind submitted values to typed FastAPI query or form parameters. |
| `st.columns` | `Grid` or `Inline` | Compose child components explicitly. |
| `st.metric` | `Metric` | Pass the label, formatted value, and optional delta. |
| `st.dataframe` | `DataTable` | Declare a `Model` when stable column types matter. Use `DataEditor` for edits. |
| `st.line_chart` | `LineChart` | Install `hedron-charts`; provide a title and accessible description. |
| `st.plotly_chart` | `PlotlyChart` | Hedron compiles the supported figure through its chart adapter. |
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
[Charts and HTMX](charts-and-htmx.md).
