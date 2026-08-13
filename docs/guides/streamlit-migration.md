# Migrate a Streamlit app

If you know Streamlit, start here. You can keep your Python data, models, SQL, and domain
logic. The part you will redesign is the interface boundary: Streamlit widgets participate
in script execution; Hedron controls submit HTTP requests to explicit page, fragment, and
action routes.

!!! info "Modern Streamlit has more than full-script reruns"

    By default, Streamlit reruns the script when a user changes a widget. Streamlit forms
    batch changes into one rerun, and `st.fragment` can rerun only a portion. Hedron still
    uses a different model: every interaction is an ordinary HTTP request with typed
    inputs and an explicit response. See Streamlit's official
    [execution-flow](https://docs.streamlit.io/develop/api-reference/execution-flow),
    [forms](https://docs.streamlit.io/develop/concepts/architecture/forms), and
    [fragments](https://docs.streamlit.io/develop/concepts/architecture/fragments)
    documentation.

## Choose your path

| Your question | Start here |
|---|---|
| Is Hedron a good fit for this app? | [Should you migrate?](#should-you-migrate) |
| Can I convert one small app end to end? | [Worked migration: sales dashboard](#worked-migration-sales-dashboard) |
| What replaces reruns, callbacks, and `st.session_state`? | [Execution and state](streamlit-execution-state.md) |
| What replaces a specific `st.*` API? | [Component migration matrix](streamlit-migration-matrix.md) |
| How do I test, deploy, and cut over safely? | [Production cutover](streamlit-cutover.md) |
| Can I run a finished migration? | [`examples/streamlit-migration`](https://github.com/eddiethedean/hedron/tree/main/examples/streamlit-migration) |

## Should you migrate?

Hedron is a strong candidate when the app is becoming a maintained web application:

- filters should have shareable, bookmarkable URLs;
- writes need explicit authorization, validation, CSRF protection, and audit boundaries;
- the team wants FastAPI dependencies, middleware, JSON routes, or OpenAPI beside the UI;
- multiple developers need reusable typed components and ordinary pytest coverage;
- deployment must fit an existing ASGI, container, proxy, or enterprise platform;
- whole-script work is becoming slow, hard to reason about, or difficult to isolate.

Staying on Streamlit is often the better choice when the app is a short-lived analysis,
the notebook-style top-to-bottom loop is the main benefit, Streamlit Community Cloud is
an essential managed dependency, or the app relies heavily on Streamlit-only components
that have no acceptable Hedron replacement. Hedron is not a drop-in compatibility layer.

## A low-risk migration plan

Do not begin by translating every `st.*` call. Migrate one user workflow:

1. **Record current behavior.** List pages, inputs, outputs, callbacks, session keys,
   cache entries, secrets, data writes, and external components. Add a small Streamlit
   `AppTest` suite around the critical workflow before changing it.
2. **Extract framework-free logic.** Move data loading, filtering, calculations, and
   writes into ordinary functions or services with no `streamlit` imports.
3. **Port the read-only result.** Return a Hedron `Page` containing headings, metrics,
   tables, and layout components.
4. **Port filters as a GET form.** Use typed query parameters first. The result works
   without JavaScript and the URL becomes shareable.
5. **Port writes as actions.** Turn `if st.button(...):` side effects into explicit POST
   actions with validation, authorization, and CSRF.
6. **Assign every piece of state an owner.** Choose URL, request/form, session, database,
   cache, or browser preference deliberately; do not copy `st.session_state` wholesale.
7. **Add fragments only where useful.** Once the full-page flow works, use HTMX to update
   expensive or frequently changing regions independently.
8. **Run both apps during acceptance.** Compare the same fixtures and user outcomes,
   then follow the [production cutover checklist](streamlit-cutover.md).

## Can I migrate incrementally?

Yes—at the workflow or URL level, not by mixing the two rendering runtimes inside one page.
The safest arrangement is:

```text
shared Python package
  ├─ data access, calculations, models, and business rules
  ├─ current Streamlit entrypoint
  └─ new Hedron ASGI app
```

Run Streamlit and Hedron as separate processes during acceptance. Put the Hedron candidate
on a staging hostname or route traffic to migrated paths at the reverse proxy. This keeps
rollback simple and lets both interfaces call the same framework-free services.

Do not try to import a Streamlit page and render it as a Hedron component. Do not let both
applications perform the same production write unless you have deliberately designed and
tested dual-write reconciliation.

## What carries over

Your pandas/Polars transformations, Pydantic models, SQLAlchemy repositories, API clients,
plotting inputs, and business rules can usually stay. The easiest migrations first isolate
these functions from `st.*` calls, then invoke them from Hedron routes. Rewriting working
domain logic and the UI at the same time creates unnecessary risk.

## What will feel different

| Streamlit habit | Hedron habit |
|---|---|
| Read a value from a widget call | Receive a typed value in a route/action parameter |
| Let an interaction rerun code | Send a GET or POST to the route that owns the operation |
| Emit UI as the script executes | Return an explicit component tree |
| Keep unrelated values in Session State | Give URL, request, session, database, cache, and browser state separate owners |
| Put logic beneath `if st.button(...)` | Put the mutation in an authorized POST action |
| Cache a resource globally | Create it in FastAPI lifespan and inject it |
| Deploy an entrypoint to Community Cloud | Build and run a portable ASGI application |

This is more architecture than a small Streamlit script needs. It becomes valuable when
the app needs stable URLs, explicit security boundaries, integration with existing backend
services, multiple contributors, or conventional production operations.

## Worked migration: sales dashboard

This guide rewrites a small sales dashboard with filters, metrics, and a table. On Hedron
**0.25.1+**, install `hedron[charts]>=0.34.0,<0.35` for Matplotlib charts; or keep
`Metric` + `DataTable` when charts are optional.

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
uv add "hedron[data]>=0.34.0,<0.35" "uvicorn[standard]"
```

To include charts, install the compatible satellite through the flagship extra:

```bash
uv add "hedron[charts]>=0.34.0,<0.35"
```

This enforces `hedron-charts>=0.1.10,<0.2`; see
[Compatibility](../COMPATIBILITY.md#charts-and-sample-kit-compatibility-floor).

Create `app.py`:

```python title="app.py"
import os
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
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only-change-me"),
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

### Add a chart

After installing the charts extra, you can replace the month `Table` with `LineChart`:

```python
from hedron_charts import LineChart

LineChart(
    [row.model_dump() for row in filtered],
    x="month",
    y="revenue",
    title="Revenue by month",
    description="Monthly revenue for the selected region and minimum.",
)
```

Details: [Charts and HTMX](charts-and-htmx.md).

## How the concepts map

| Streamlit | Hedron | Migration note |
|---|---|---|
| `st.title`, `st.write` | `Heading`, `Text`, `Markdown`, or `Auto` | Return components from a page route instead of emitting them as side effects. |
| `st.sidebar` | `Sidebar` | A sidebar is an explicit child in the page layout. |
| `st.selectbox`, `st.slider` | `Select` or native controls inside `Form` | Bind submitted values to typed FastAPI query or form parameters. |
| `st.columns` | `Grid` or `Inline` | Compose child components explicitly. |
| `st.metric` | `Metric` | Pass the label, formatted value, and optional delta. |
| `st.dataframe` | `DataTable` | Declare a `Model` when stable column types matter. Use `DataEditor` for edits. |
| `st.line_chart` | `LineChart` (`hedron[charts]>=0.34.0,<0.35`) | Provide a title and accessible description; a table fallback remains useful. |
| `st.plotly_chart` | `PlotlyChart` (experimental) | Hedron compiles the figure through its bounded chart adapter. |
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

## Common migration surprises

| Symptom | Likely cause | Fix |
|---|---|---|
| A filter does nothing until **Apply** is selected | Hedron controls submit; they do not return live Python values | Keep the deliberate form submit, or add a GET fragment for justified immediate updates |
| Fragment request returns 403 | `HX-Target` does not match the route's declared region | Use `app.region(...)` and region-aware controls; check the id/selector |
| POST returns a CSRF error | The form did not carry the token seeded by the page GET | Start with [Minimal form POST](minimal-form.md); do not disable CSRF to imitate a callback |
| Query returns 422 | FastAPI rejected an invalid typed value or bound | Correct the form value and render friendly validation guidance for the workflow |
| `DataTable` cannot be imported | The data extra is not installed | Install `hedron[data]` at the same 0.25 version as `hedron` |
| A private cache never hits | Sensitive scopes require concrete `vary_on` dimensions | Pass the user/tenant/session key as a function argument and include its name in `vary_on` |
| Chart installation resolves an older core | The lower bound allowed a satellite before `0.1.6` | Install `hedron[charts]>=0.34.0,<0.35` in a clean environment |
| State disappears after deployment/restart | Process/session memory was treated as durable storage | Move durable state to a database or shared service and review the multi-worker model |

## Migration checkpoint

Before converting another screen, verify that this first workflow has preserved the user
outcome rather than the original implementation:

- the default dashboard totals match the Streamlit app;
- each filter produces the same rows and totals;
- filter values survive refresh because they are present in the URL;
- an empty result is understandable and accessible;
- invalid query values receive a clear validation response;
- the route can be tested with FastAPI `TestClient` without a browser;
- no user-specific data is stored in a public cache entry.

Then choose the next topic by migration pressure:

- callbacks, fragments, or state: [Execution and state](streamlit-execution-state.md);
- API lookup: [Streamlit → Hedron matrix](streamlit-migration-matrix.md);
- mutations: [Forms and actions](forms-and-actions.md);
- deployment and rollback: [Production cutover](streamlit-cutover.md).
