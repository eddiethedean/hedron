"""0.50.1 patch: confirmed code defects."""

from __future__ import annotations

import builtins
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from tests.unit._helpers_050 import reset_050

from hedron_core.builtins.controls import Button, IconButton, LinkButton
from hedron_core.builtins.shell import HtmxLink
from hedron_core.dashboard import DashboardBinding, InteractionGraph
from hedron_core.diagnostics import HedronError
from hedron_core.htmx.attrs import Hx
from hedron_core.htmx_contract import safe_css_selector
from hedron_core.plugins import ExplorerProvider, register_explorer_provider
from hedron_core.rendering import render
from hedron_core.visualization import ChartAccessibility
from hedron_data.advanced import evaluate_formula
from hedron_data.spreadsheet import _reject_or_sanitize
from hedron_elements.action_async import ActionAsync
from hedron_elements.dialog import Dialog
from hedron_elements.disclosure import Disclosure
from hedron_elements.field_choice import FieldChoice
from hedron_elements.field_file import FieldFile
from hedron_elements.field_text import FieldText


def test_formula_combining_mark_prefix_is_rejected() -> None:
    payload = "\u0300=SUM(1)"
    with pytest.raises(HedronError, match="HED-DATA-0040"):
        _reject_or_sanitize(payload, formula_policy="reject")
    assert _reject_or_sanitize(payload, formula_policy="sanitize").startswith("'")


def test_hx_and_htmx_link_accept_relative_this() -> None:
    assert safe_css_selector("this") is True
    attrs = Hx(target="this", indicator="this").as_html_attrs()
    assert attrs["hx-target"] == "this"
    assert attrs["hx-indicator"] == "this"
    html = render(HtmxLink("Go", "/panel", target="this")).html
    assert 'hx-target="this"' in html


def test_evaluate_formula_rejects_non_numeric_cells() -> None:
    with pytest.raises(HedronError, match="HED-DATA-0032"):
        evaluate_formula("=[flag]*2", {"flag": True})
    with pytest.raises(HedronError, match="HED-DATA-0032"):
        evaluate_formula("=[qty]+1", {"qty": None})
    with pytest.raises(HedronError, match="HED-DATA-0032"):
        evaluate_formula("=[label]+1", {"label": "n/a"})


def test_chart_host_tabular_fallback_renders_cells() -> None:
    from hedron.testing import render_html
    from hedron_charts.optional_adapters import ChartJsAdapter

    acc = ChartAccessibility(
        title="t",
        description="d",
        tabular_fallback=[{"a": 1, "b": 2}],
    )
    output = ChartJsAdapter().compile({"type": "bar", "data": {}}, accessibility=acc)
    html = render_html(ChartJsAdapter().render_node(output))
    assert "hedron-chart-fallback" in html
    assert "<td>1</td>" in html
    assert "<td>2</td>" in html


def test_beginner_svg_fallback_keeps_negative_y_in_viewbox(monkeypatch: pytest.MonkeyPatch) -> None:
    from hedron_charts.compile import beginner_to_spec, compile_chart
    from hedron_charts.components import _xy_fallback_figure
    from hedron_charts.export import export_svg

    real_import = builtins.__import__

    def _no_matplotlib(name: str, *args: object, **kwargs: object):
        if name == "matplotlib" or name.startswith("matplotlib."):
            raise ImportError("forced")
        return real_import(name, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(builtins, "__import__", _no_matplotlib)
    html = render(
        _xy_fallback_figure(
            data=[{"x": 0, "y": -4}, {"x": 1, "y": 2}],
            x="x",
            y="y",
            title="Neg",
            description="negative domain",
            alt="chart",
            waiver=None,
            limits=None,
            kind="scatter",
        )
    ).html
    monkeypatch.undo()
    assert "cy=" in html
    assert 'cy="-' not in html
    spec = beginner_to_spec(
        kind="line",
        data=[{"x": 0, "y": -4}, {"x": 1, "y": 2}],
        x="x",
        y="y",
        title="Neg",
        description="negative domain",
    )
    svg = export_svg(compile_chart(spec))
    assert ",-" not in svg


def test_great_tables_supports_native_objects_only() -> None:
    from hedron_charts.optional_adapters import GreatTablesAdapter

    adapter = GreatTablesAdapter()
    assert adapter.supports([{"a": 1}]) is False
    compiled = adapter.compile(
        [{"a": 1}],
        accessibility=ChartAccessibility(title="t", description="d"),
    )
    assert compiled.metadata is not None
    assert compiled.metadata.get("adapter") == "great-tables"


def test_missing_extra_pin_matches_current_train() -> None:
    from hedron.cli.discovery import _release_pin_bounds
    from hedron_charts.limits import missing_extra

    floor, ceiling = _release_pin_bounds()
    err = missing_extra("plotly")
    assert f"hedron[charts]>={floor},<{ceiling}" in err.diagnostic.remediation
    assert "0.38.0" not in err.diagnostic.remediation


def test_button_link_icon_accept_id() -> None:
    assert 'id="save-btn"' in render(Button("Save", id="save-btn")).html
    assert 'id="go-link"' in render(LinkButton("Go", "/next", id="go-link")).html
    assert 'id="icon-1"' in render(IconButton("Menu", icon="☰", id="icon-1")).html


def test_element_frozen_markup_keeps_abi_attrs() -> None:
    file_markup = FieldFile(
        name="doc", accept=".pdf", multiple=True, required=True, disabled=True
    ).render_markup()
    assert "accept=" in file_markup
    assert "multiple=" in file_markup
    assert "required=" in file_markup
    assert "disabled=" in file_markup

    text_markup = FieldText(
        "title", value="Hi", label="Title", required=True, disabled=True, input_type="email"
    ).render_markup()
    assert "required=" in text_markup
    assert "disabled=" in text_markup
    assert "label=" in text_markup
    assert "input-type=" in text_markup

    choice_markup = FieldChoice("opt", (("a", "A"),), required=True, disabled=True).render_markup()
    assert "required=" in choice_markup
    assert "disabled=" in choice_markup

    assert "open=" in Disclosure("More", open=True).render_markup()
    assert "open=" in Dialog("Confirm", open=True).render_markup()


def test_action_async_emits_hx_target() -> None:
    html = render(ActionAsync("Run", hx_post="/run", hx_target="this")).html
    assert 'hx-target="this"' in html
    markup = ActionAsync("Run", hx_post="/run", hx_target="#panel").render_markup()
    assert 'hx-target="#panel"' in markup
    with pytest.raises(ValueError, match="Unsafe HTMX target"):
        ActionAsync("Run", hx_post="/run", hx_target="javascript:alert(1)")


def test_explorer_dashboard_graph_reads_app_state() -> None:
    reset_050()
    graph = InteractionGraph()
    graph.declare_inputs("chart.select")
    graph.register(
        DashboardBinding(
            id="filter-panel",
            triggers=("chart.select",),
            snapshot_inputs=(),
            targets=("main-panel",),
            action_id="apply_filters",
        )
    )
    app = FastAPI()
    app.state.hedron_dashboard_graph = graph
    from hedron_explorer.router import explorer_router

    app.include_router(explorer_router(), prefix="/hedron-explorer")
    client = TestClient(app)
    empty_app = FastAPI()
    empty_app.include_router(explorer_router(), prefix="/hedron-explorer")
    empty = TestClient(empty_app).get("/hedron-explorer/api/dashboard-graph").json()
    assert empty["nodes"] == []
    body = client.get("/hedron-explorer/api/dashboard-graph").json()
    assert any(node.get("id") == "filter-panel" for node in body["nodes"])
    assert body["stability"] == "experimental"


def test_explorer_packages_renders_provider_nodes() -> None:
    reset_050()
    from hedron_core.html import html

    register_explorer_provider(
        ExplorerProvider(
            panel_id="demo-html",
            title="Demo",
            plugin="test",
            render=lambda: html.p("hello-panel"),
        )
    )
    app = FastAPI()
    from hedron_explorer.router import explorer_router

    app.include_router(explorer_router(), prefix="/hedron-explorer")
    page = TestClient(app).get("/hedron-explorer/packages")
    assert page.status_code == 200
    assert "hello-panel" in page.text
    assert "&lt;p" not in page.text


def test_explorer_maps_shows_plan_facts() -> None:
    reset_050()
    app = FastAPI()
    from hedron_explorer.router import explorer_router

    app.include_router(explorer_router(), prefix="/hedron-explorer")
    page = TestClient(app).get("/hedron-explorer/maps")
    assert page.status_code == 200
    assert "MapPlan facts" in page.text
    assert "origins" in page.text
    assert "attribution" in page.text


def test_explorer_security_lists_audit_tail() -> None:
    reset_050()
    from hedron_explorer.services.runtime import audit

    audit("probe", path="/hedron-explorer/security")
    app = FastAPI()
    from hedron_explorer.router import explorer_router

    app.include_router(explorer_router(), prefix="/hedron-explorer")
    page = TestClient(app).get("/hedron-explorer/security")
    assert page.status_code == 200
    assert "Audit tail" in page.text
    assert "probe" in page.text or "request" in page.text


def test_explorer_fastapi_extra_matches_base_cap() -> None:
    text = Path("packages/hedron-explorer/pyproject.toml").read_text(encoding="utf-8")
    assert text.count("fastapi>=0.121.0,<0.150") == 2
    assert "fastapi>=0.121.0,<0.142" not in text


def test_hx_still_rejects_unsafe_selectors() -> None:
    assert safe_css_selector("#ok") is True
    assert safe_css_selector("javascript:alert(1)") is False
    with pytest.raises(ValueError):
        Hx(target="javascript:alert(1)").as_html_attrs()


def test_dashboard_graph_json_uses_request_state() -> None:
    from hedron_explorer.services.catalog import dashboard_graph_json

    graph = InteractionGraph()
    graph.declare_inputs("grid.select")
    request = SimpleNamespace(
        app=SimpleNamespace(state=SimpleNamespace(hedron_dashboard_graph=graph)),
        query_params={},
    )
    payload = dashboard_graph_json(request)  # type: ignore[arg-type]
    assert any(node.get("id") == "grid.select" for node in payload["nodes"])
