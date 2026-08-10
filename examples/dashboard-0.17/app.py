"""Minimal analytical reference app for phase 0.17 exit scenarios."""

from __future__ import annotations

from hedron import Hedron, InteractionResult, swap
from hedron_core import AppShell, HtmxLink, MainPanel, Text, render
from hedron_core.dashboard import DashboardBinding, InteractionGraph
from hedron_core.interaction import FragmentRegion, InteractionPolicy
from hedron_core.patches import PropertyPatch, apply_property_patch

app = Hedron()
POLICY = InteractionPolicy(
    declared_regions=(FragmentRegion(id="main-panel", selector="#main-panel"),),
    allow_undeclared_targets=False,
)

GRAPH = InteractionGraph()
GRAPH.declare_inputs("chart.select", "grid.select", "map.viewport")
GRAPH.register(
    DashboardBinding(
        id="filter-panel",
        triggers=("chart.select", "grid.select"),
        snapshot_inputs=(),
        targets=("main-panel",),
        action_id="apply_filters",
        debounce_ms=50,
    )
)

_STATE: dict[str, object] = {"dashboard": {"_version": 0, "filter": None}}


@app.page("/")
def home() -> AppShell:
    dash = _STATE["dashboard"]
    assert isinstance(dash, dict)
    return AppShell(
        nav=(
            HtmxLink("Dashboard", "/", target="#main-panel", select="#main-panel", push_url=True),
            HtmxLink(
                "Panel",
                "/panel",
                target="#main-panel",
                select="#main-panel",
                push_url=True,
            ),
        ),
        body=MainPanel(
            Text("Cross-filter dashboard (0.17 reference)"),
            Text(f"Filter={dash.get('filter')!r}"),
        ),
    )


@app.page("/panel")
def panel() -> MainPanel:
    return MainPanel(Text("Dynamic panel"), id="main-panel")


@app.component("/actions/apply-filters", methods=["POST"])
def apply_filters() -> InteractionResult:
    global _STATE
    try:
        _STATE = apply_property_patch(
            _STATE,
            PropertyPatch(target_id="dashboard", path="filter", op="assign", value="active"),
        )
    except Exception:  # noqa: BLE001
        return swap(MainPanel(Text("Full fragment fallback"), id="main-panel"), policy=POLICY)
    dash = _STATE["dashboard"]
    assert isinstance(dash, dict)
    return swap(
        MainPanel(Text(f"Filter={dash.get('filter')!r}"), id="main-panel"),
        policy=POLICY,
    )


def graph_snapshot() -> list[str]:
    return list(GRAPH.topological_order())


if __name__ == "__main__":
    print(render(home()).html[:200])
    print("bindings", graph_snapshot())
