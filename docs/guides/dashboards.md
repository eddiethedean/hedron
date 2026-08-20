# Dashboards and interaction graphs

Phase **0.17** shipped page-local dashboard bindings and finite interaction graphs for
reactive admin / data UIs. Capability readiness is **Supported** on the living **0.53**
train (feature introduced in 0.17); API compatibility remains **`beta`** — pin
`hedron>=0.52.0,<0.53`.

## Start here

| Need | Where |
|---|---|
| What shipped and honesty limits | [What's new in 0.17](whats-new-0.17.md) |
| Dash callback mapping | [Dash migration](dash-migration.md) |
| NiceGUI refreshable mapping | [NiceGUI migration](nicegui-migration.md) |
| Maintainer exit stub | [`examples/dashboard-0.17`](https://github.com/eddiethedean/hedron/tree/main/examples/dashboard-0.17) |
| Generated signatures | [Autodoc — Dashboards](../api/AUTODOC.md#dashboards-017) |

## Mental model

- Prefer **`DashboardBinding` / `InteractionGraph` / `TriggerContext`** over ad-hoc
  multi-region wiring — graphs are page-local and fail closed on cycles / duplicate writers.
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

## Minimal graph (runnable shape)

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


@app.page("/")
def home() -> Text:
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
  [0.17 dashboard release notes](whats-new-0.17.md#upgrade-notes)
