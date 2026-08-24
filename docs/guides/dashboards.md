# Dashboards and interaction graphs

Prefer **`DashboardWorkspace`** for validated filters, one request-bound loader, and named
render-only panels (phase **0.60**). Phase **0.17** `DashboardBinding` /
`InteractionGraph` remain available as Advanced linked-interaction primitives.

Capability readiness is **Supported** on the living **0.63.x** train; API compatibility
remains **`beta`** — pin `hedron>=0.63.0,<0.64` from PyPI (published as `v0.63.0`).

## Start here

| Need | Where |
|---|---|
| Progressive dashboard facade | This page (`DashboardWorkspace`) |
| What shipped in 0.60 | [What's new in 0.60](whats-new-0.60.md) |
| What shipped in 0.17 | [What's new in 0.17](whats-new-0.17.md) |
| Dash callback mapping | [Dash migration](dash-migration.md) |
| NiceGUI refreshable mapping | [NiceGUI migration](nicegui-migration.md) |
| Generated signatures | [Autodoc — Dashboards](../api/AUTODOC.md#dashboards-017) |

## Golden path — `DashboardWorkspace`

```python
import os

from pydantic import BaseModel, Field

from hedron import DashboardWorkspace, DesignSystem, Hedron, Text

design = DesignSystem.brand("sales", accent="#0f766e")

app = Hedron(
    title="Sales dashboard",
    security="standard",
    explorer="off",
    theme=design,
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "replace-in-production"),
)


class Filters(BaseModel):
    region: str = "all"
    limit: int = Field(default=5, ge=1, le=50)


class DashData(BaseModel):
    region: str
    total: int


def load_dashboard(filters: Filters) -> DashData:
    # Synthetic loader — replace with authorized IO and caching policy in production.
    base = 42 if filters.region == "all" else 7
    return DashData(region=filters.region, total=base * filters.limit)


def summary_panel(data: DashData) -> object:
    return Text(f"{data.region}: {data.total}")


dashboard = DashboardWorkspace(
    name="sales",
    path="/sales",
    title="Sales",
    filters=Filters,
    load=load_dashboard,
    panels={"summary": summary_panel},
)
app.include_feature(dashboard)


@app.screen("/", title="Home")
def home():
    return Text("Open /sales for the DashboardWorkspace. Replace loader/auth for production.")
```

Or scaffold with `hedron new NAME --template dashboard`.

## Mental model

- Prefer **`DashboardWorkspace`** for ordinary filter → load → panel composition.
- Prefer **`DashboardBinding` / `InteractionGraph` / `TriggerContext`** (Advanced) for
  multi-writer linked interactions — graphs are page-local and fail closed on cycles /
  duplicate writers.
- **`PropertyPatch` / `CollectionPatch`** provide versioned incremental updates with
  full-fragment fallback when a patch cannot apply.
- Cross-filter and recorder/replay compose chart/grid/map viewport triggers; do not rely
  on sleep-based races in tests. On **0.39**, prefer `compose_chartlink_039` so table
  selection consumes Published `hedron-chart` events without a parallel renderer
  ([DATA.md](../api/DATA.md)).
- Live SSE/WebSocket transports remain **experimental** — prefer HTMX **polling** /
  fragment refresh for Supported production paths ([live interaction](live-interaction.md)).

## Try a cross-filter (simulated)

This compact example shows the user-facing result of one page-local filter writing to one
declared table region. The production graph still owns dependency ordering, duplicate-writer
checks, authorization, and the action that supplies the rows.

=== "Demo"

    Use page-local controls to cross-filter one declared table region. Docs simulation.

    <!-- hedron-sim:data-table-filter -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    import os

    from hedron import Hedron, Page, Stack, html, swap

    app = Hedron(
        title="People",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    table = app.region("people-table", description="People table")

    ROWS = (
        ("1", "Ada", "admin"),
        ("2", "Grace", "member"),
        ("3", "Katherine", "admin"),
        ("4", "Margaret", "member"),
    )


    def table_panel(filter_role: str | None = None):
        filtered = [r for r in ROWS if filter_role is None or r[2] == filter_role]
        label = "All people" if filter_role is None else f"Role: {filter_role}"
        return html.div(
            html.strong(label),
            html.table(
                html.thead(html.tr(html.th("ID"), html.th("Name"), html.th("Role"))),
                html.tbody(*[html.tr(html.td(a), html.td(b), html.td(c)) for a, b, c in filtered]),
            ),
            id=table.id,
        )


    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                table_panel(),
                html.button(
                    "All",
                    type="button",
                    **{"hx-get": "/rows", "hx-target": table.selector, "hx-swap": "outerHTML"},
                ),
                html.button(
                    "Admins",
                    type="button",
                    **{"hx-get": "/rows/admin", "hx-target": table.selector, "hx-swap": "outerHTML"},
                ),
                html.button(
                    "Members",
                    type="button",
                    **{"hx-get": "/rows/member", "hx-target": table.selector, "hx-swap": "outerHTML"},
                ),
            ),
            title="People",
        )


    @app.fragment("/rows", region=table)
    def all_rows():
        return swap(table_panel())


    @app.fragment("/rows/admin", region=table)
    def admin_rows():
        return swap(table_panel("admin"))


    @app.fragment("/rows/member", region=table)
    def member_rows():
        return swap(table_panel("member"))
    ```

## Advanced — interaction graph

Register inputs and bindings before serving. Empty targets, duplicate ids, missing
dependencies, and cycles raise `DashboardGraphError` (`HED-GRAPH-0001` … `0005`).

```python
from hedron import Hedron, Text
from hedron_core.dashboard import DashboardBinding, InteractionGraph

app = Hedron(
    title="Dashboard sketch",
    security="standard",
    explorer="off",
    session_secret="replace-in-production",
)

graph = InteractionGraph()
graph.declare_inputs("chart.select", "grid.select")
graph.register(
    DashboardBinding(
        id="filter-panel",
        triggers=("chart.select", "grid.select"),
        snapshot_inputs=(),
        targets=("main-panel",),
        action_id="apply_filters",
        debounce_ms=50,
    )
)


@app.screen("/", title="Home")
def home():
    order = ", ".join(graph.topological_order())
    return Text(f"Bindings in order: {order}")
```

Wire `action_id` to your own `@app.action` / fragment handlers and declared
`FragmentRegion`s — see the [dashboard-0.17 stub](https://github.com/eddiethedean/hedron/tree/main/examples/dashboard-0.17)
for AppShell + `InteractionResult` wiring.

## Errors

| Condition | Behavior |
|---|---|
| Empty / duplicate binding id | `DashboardGraphError` (`HED-GRAPH-0005`) |
| Empty `targets` | `HED-GRAPH-0004` |
| Cycle / missing dependency / duplicate writers | Fail closed at `register` (`HED-GRAPH-0001`–`0003`) |

## Not Dash / Streamlit

There is no global callback DAG, no automatic JS conversion, and no notebook-style full
rerun model. Map concepts via the migration guides above, then keep authorization and
tenant isolation in your host app ([multi-tenant](multi-tenant.md)).

## Next

- [Compose built-ins](component-composition.md) · [Data apps](data-apps.md) ·
  [0.60 release notes](whats-new-0.60.md) · [0.17 dashboard notes](whats-new-0.17.md#upgrade-notes)
