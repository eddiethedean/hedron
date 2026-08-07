# Dashboards and interaction graphs

Phase **0.17** shipped page-local dashboard bindings and finite interaction graphs for
reactive admin / data UIs. Capability readiness is **Supported** on the 0.18 train; API
compatibility remains **`beta`** — pin `hedron>=0.18.0,<0.19`.

## Start here

| Need | Where |
|---|---|
| What shipped and honesty limits | [What's new in 0.17](whats-new-0.17.md) |
| Dash callback mapping | [Dash migration](dash-migration.md) |
| NiceGUI refreshable mapping | [NiceGUI migration](nicegui-migration.md) |
| Maintainer exit stub | [`examples/dashboard-0.17`](https://github.com/eddiethedean/hedron/tree/main/examples/dashboard-0.17) |

## Mental model

- Prefer **`DashboardBinding` / `InteractionGraph` / `TriggerContext`** over ad-hoc
  multi-region wiring — graphs are page-local and fail closed on cycles / duplicate writers.
- **`PropertyPatch` / `CollectionPatch`** provide versioned incremental updates with
  full-fragment fallback when a patch cannot apply.
- Cross-filter and recorder/replay compose chart/grid/map viewport triggers; do not rely
  on sleep-based races in tests.
- Live SSE/WebSocket transports remain **experimental** — prefer HTMX **polling** /
  fragment refresh for Supported production paths ([live interaction](live-interaction.md)).

```python
# Conceptual shape — see what's-new-0.17 and the dashboard-0.17 stub for wiring.
from hedron_core import DashboardBinding, InteractionGraph  # noqa: F401
```

## Not Dash / Streamlit

There is no global callback DAG, no automatic JS conversion, and no notebook-style full
rerun model. Map concepts via the migration guides above, then keep authorization and
tenant isolation in your host app ([multi-tenant](multi-tenant.md)).

## Next

- [Compose built-ins](component-composition.md) · [Data apps](data-apps.md) ·
  [Upgrade](upgrade.md#017-reactive-dashboards-and-agent-interfaces-published)
