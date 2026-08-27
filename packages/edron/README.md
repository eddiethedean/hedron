# Edron

Edron is a class-oriented Python authoring facade over Hedron. It keeps Hedron as the renderer,
router, interaction, state, styling, and security authority.

```python
import edron as ed

app = ed.App(title="Hello")


@app.page("/", title="Hello")
class Home(ed.Page):
    def render(self) -> None:
        self.heading("Hello, Edron")
        self.text("A small Python vocabulary over native Hedron.")
```

Edron 0.5 is an in-tree Beta implementation line. Native Hedron objects remain available through
`app.hedron` and `Page.include()`. Use `edron check` for non-executing editor feedback,
`edron explain` for source-mapped registration facts, and `edron new` for teaching scaffolds.

Phase 0.5 adds explicit resource lifetimes, native-backed cache policy, durable job wiring, and
deployment diagnostics without creating a second registry or worker runtime:

```python
db = app.resource("database", create_database, secret_refs={"dsn": "DATABASE_URL"})


@ed.cache_data(ttl=60, scope="tenant", vary_on=("tenant_id",))
def load_summary(tenant_id: str) -> dict[str, int]:
    return query_summary(db, tenant_id)
```

Resources are lazy and closed by the native app lifespan. `app.operations()` reports backend
durability and resource metadata without resolving factories or exposing secrets. `JobFlow` keeps
polling and ordinary HTTP as the correctness baseline; optional live observations are native SSE
projections with the same authorization and no-JavaScript fallback.

Phase 0.4 adds explicit visualization and media composition while keeping native Hedron as the
rendering and security authority:

```python
from pydantic import BaseModel
from hedron_charts import Chart, beginner_to_spec

chart = Chart(
    spec=beginner_to_spec(
        kind="line",
        data=rows,
        x="month",
        y="revenue",
        title="Revenue",
        description="Revenue by month",
    )
)


@app.page("/sales", title="Sales")
class Sales(ed.Page):
    def render(self) -> None:
        self.chart(chart, alternative="The table below contains the exact values.")
        self.image("/assets/sales.png", alt="Revenue trend")
```

Typed chart/map links are registered with `app.chart_interaction(...)` or
`app.map_interaction(...)`; they lower to native `ChartInteraction`/`MapInteraction` bundles and
never execute client callbacks. Selection payloads remain bounded, typed, and subject to the
native authorization and CSRF policies.

Data workspaces are explicit and application-owned:

```python
columns = (ed.Column("id", read_only=True), ed.Column("name", writable=True))
source = ed.DataSource.in_memory(
    [{"id": "1", "name": "Ada"}],
    columns=columns,
    writable_fields=("name",),
)
workspace = ed.DataWorkspace("people", source=source, columns=columns)
```

Add an `EditPolicy` with explicit authorization to make a workspace editable. Edron never owns
database sessions, transactions, authorization state, persistence, or audit storage.
