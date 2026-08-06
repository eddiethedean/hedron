"""Phase 0.17 GRAPH-017: InteractionGraph registration and ordering."""

from __future__ import annotations

import pytest

from hedron_core import (
    DashboardBinding,
    DashboardGraphError,
    InteractionGraph,
    TriggerContext,
)
from hedron_core.codes import HED_GRAPH_0002, HED_GRAPH_0003


def _binding(
    bid: str,
    *,
    triggers: tuple[str, ...] = ("input",),
    targets: tuple[str, ...] = ("out",),
    action_id: str = "act",
    snapshot_inputs: tuple[str, ...] = (),
) -> DashboardBinding:
    return DashboardBinding(
        id=bid,
        triggers=triggers,
        snapshot_inputs=snapshot_inputs,
        targets=targets,
        action_id=action_id,
    )


def test_register_success_and_topo_order() -> None:
    graph = InteractionGraph()
    graph.declare_inputs("filter")
    graph.register(
        _binding("b1", triggers=("filter",), targets=("chart",), action_id="filter_chart")
    )
    graph.register(_binding("b2", triggers=("chart",), targets=("table",), action_id="chart_table"))

    order = graph.topological_order()
    assert order == ["b1", "b2"]

    ctx = TriggerContext(
        binding_id="b1",
        event_source="change",
        component_id="filter",
        changed_fields=("value",),
        correlation_id="c-1",
        snapshots={"filter": {"value": "x"}},
    )
    assert ctx.binding_id == "b1"
    assert ctx.snapshots["filter"] == {"value": "x"}


def test_cycle_fails_registration() -> None:
    graph = InteractionGraph()
    # Declare both so registration can proceed to cycle detection.
    graph.declare_inputs("x", "y")
    graph.register(_binding("a", triggers=("y",), targets=("x",)))
    with pytest.raises(DashboardGraphError, match="Cycle") as excinfo:
        graph.register(_binding("b", triggers=("x",), targets=("y",)))
    assert excinfo.value.code == HED_GRAPH_0002


def test_duplicate_writer_fails() -> None:
    graph = InteractionGraph()
    graph.declare_inputs("seed")
    graph.register(_binding("a", triggers=("seed",), targets=("region",)))
    with pytest.raises(DashboardGraphError, match="Duplicate writer") as excinfo:
        graph.register(_binding("b", triggers=("seed",), targets=("region",)))
    assert excinfo.value.code == HED_GRAPH_0003


def test_empty_targets_and_missing_deps() -> None:
    graph = InteractionGraph()
    with pytest.raises(DashboardGraphError, match="empty targets"):
        graph.register(
            DashboardBinding(
                id="empty",
                triggers=("a",),
                snapshot_inputs=(),
                targets=(),
                action_id="x",
            )
        )

    with pytest.raises(DashboardGraphError, match="missing"):
        graph.register(_binding("orphan", triggers=("undeclared",), targets=("out",)))
