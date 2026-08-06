"""Phase 0.17 XFILTER-017: cross-filter composition helpers."""

from __future__ import annotations

import os

import pytest

from hedron_core import (
    MAP_VIEWPORT_TRIGGER,
    ChartEvent,
    CrossFilterBinding,
    InteractionGraph,
    compose_cross_filter,
    dashboard_graph_payload,
    triggers_from_chart_event,
    triggers_from_grid_selection,
)


def test_compose_cross_filter_registers_binding() -> None:
    graph = InteractionGraph()
    binding = compose_cross_filter(
        graph,
        chart_trigger="chart.click",
        grid_trigger="grid.selection",
        targets=("detail", "summary"),
    )
    assert binding.id == "cross_filter"
    assert binding.triggers == ("chart.click", "grid.selection")
    assert binding.targets == ("detail", "summary")
    assert graph.topological_order() == ["cross_filter"]


def test_compose_cross_filter_with_map_viewport() -> None:
    graph = InteractionGraph()
    binding = compose_cross_filter(
        graph,
        chart_trigger="chart.box",
        grid_trigger="grid.selection",
        targets=("map_panel",),
        map_viewport=True,
    )
    assert MAP_VIEWPORT_TRIGGER in binding.triggers
    assert binding.triggers == ("chart.box", "grid.selection", "map.viewport")

    graph2 = InteractionGraph()
    custom = compose_cross_filter(
        graph2,
        chart_trigger="chart.click",
        grid_trigger="grid.selection",
        targets=("out",),
        map_viewport="map.viewport",
        binding_id="xf-map",
    )
    assert custom.triggers[-1] == "map.viewport"


def test_cross_filter_binding_wires_chart_and_grid_fields() -> None:
    xf = CrossFilterBinding(
        id="xf1",
        chart_fields=("click", "hover"),
        grid_selection_fields=("selection", "row_key"),
        targets=("table", "chart"),
        map_viewport=True,
        action_id="filter_regions",
    )
    assert xf.trigger_ids() == (
        "chart.click",
        "chart.hover",
        "grid.selection",
        "grid.row_key",
        "map.viewport",
    )
    graph = InteractionGraph()
    binding = xf.register(graph)
    assert binding.action_id == "filter_regions"
    assert "map.viewport" in graph.declared_inputs


def test_triggers_from_chart_and_grid_helpers() -> None:
    event = ChartEvent(kind="click", trace_id="t1", payload={"x": 1})
    assert triggers_from_chart_event(event) == ("chart.click",)
    assert triggers_from_chart_event(event, fields=("select",)) == ("chart.select",)
    assert triggers_from_grid_selection() == ("grid.selection",)
    assert triggers_from_grid_selection(fields=("selectedRows",)) == ("grid.selectedRows",)


def test_dashboard_graph_payload_has_nodes_and_edges() -> None:
    graph = InteractionGraph()
    compose_cross_filter(
        graph,
        chart_trigger="chart.click",
        grid_trigger="grid.selection",
        targets=("detail",),
        map_viewport=True,
    )
    payload = dashboard_graph_payload(graph)
    assert "nodes" in payload and "edges" in payload
    node_ids = {n["id"] for n in payload["nodes"]}  # type: ignore[index]
    assert "cross_filter" in node_ids
    assert "chart.click" in node_ids
    assert "grid.selection" in node_ids
    assert "map.viewport" in node_ids
    assert "detail" in node_ids
    assert any(e["kind"] == "trigger" for e in payload["edges"])  # type: ignore[index]
    assert any(e["kind"] == "target" for e in payload["edges"])  # type: ignore[index]


@pytest.mark.browser
@pytest.mark.skipif(
    os.environ.get("HEDRON_BROWSER") != "1",
    reason="Opt-in: set HEDRON_BROWSER=1 for Playwright smoke",
)
def test_cross_filter_browser_smoke_placeholder() -> None:
    """Optional browser marker; unit graph composition is the Verified gate path."""
    graph = InteractionGraph()
    compose_cross_filter(
        graph,
        chart_trigger="chart.click",
        grid_trigger="grid.selection",
        targets=("detail",),
    )
    assert graph.bindings()
