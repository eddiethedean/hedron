"""QUERY-050 search/filter/pagination and 2000-component fixture."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
from tests.unit._helpers_050 import reset_050

from hedron_core.codes import HED_EXPLORER_0001
from hedron_core.registry import register_component, register_route, reset_registry_for_tests
from hedron_explorer.router import explorer_router
from hedron_explorer.services.catalog import find_component, graph_json, routes_json


def setup_function() -> None:
    reset_050()
    reset_registry_for_tests()


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(explorer_router(), prefix="/hedron-explorer")
    return TestClient(app)


def test_large_registry_truncation_and_cursor() -> None:
    for i in range(2000):
        register_component(
            logical_id=f"demo.comp{i:04d}",
            name=f"Comp{i:04d}",
            module="demo",
            distribution="demo",
        )
    client = _client()
    first = client.get("/hedron-explorer/api/components")
    assert first.status_code == 200
    body = first.json()
    assert isinstance(body, dict)
    assert body["truncated"] is True
    assert body["total"] == 2000
    assert body["diagnostic"] == HED_EXPLORER_0001
    assert len(body["items"]) <= 200
    page = client.get("/hedron-explorer/api/components?limit=50&cursor=0")
    payload = page.json()
    assert payload["truncated"] is True
    assert payload["total"] == 2000
    assert payload["diagnostic"] == HED_EXPLORER_0001
    assert payload["next_cursor"] == "50"
    html = client.get("/hedron-explorer/?limit=50")
    assert html.status_code == 200
    assert HED_EXPLORER_0001 in html.text
    assert "rel='next'" in html.text or 'rel="next"' in html.text or "rel='next'" in html.text


def test_search_filter_sort() -> None:
    register_component(logical_id="demo.alpha", name="Alpha", module="demo", distribution="z")
    register_component(logical_id="demo.beta", name="Beta", module="demo", distribution="a")
    client = _client()
    found = client.get("/hedron-explorer/api/components?q=Alpha")
    names = [row["name"] for row in found.json()]
    assert names == ["Alpha"]
    sorted_rows = client.get("/hedron-explorer/api/components?sort=distribution")
    assert [row["name"] for row in sorted_rows.json()][0] == "Beta"


def test_cli_routes_are_not_silently_capped() -> None:
    for i in range(60):
        register_route(
            kind="page",
            logical_id=f"demo.route{i:02d}",
            name=f"route{i:02d}",
            path=f"/r{i:02d}",
            methods=("GET",),
            operation_id=f"route{i:02d}",
            include_in_schema=True,
            module="demo",
        )
    payload = routes_json()
    assert isinstance(payload, list)
    assert len(payload) == 60


def test_graph_json_includes_browser_module_edges() -> None:
    register_component(
        logical_id="demo.Widget",
        name="Widget",
        module="demo",
        distribution="demo",
        browser_modules=("demo/widget.mjs",),
        styles_path="demo/widget.css",
    )
    payload = graph_json()
    kinds = {edge["kind"] for edge in payload["edges"]}
    assert "styles" in kinds
    assert "browser_module" in kinds
    assert payload["divergence"]["cli_only"] == ["inverse_consumers"]


def test_find_component_matches_exact_logical_id() -> None:
    register_component(
        logical_id="demo.exact.Widget",
        name="Other",
        module="demo",
        distribution="demo",
    )
    found = find_component("demo.exact.Widget")
    assert found is not None
    assert found.logical_id == "demo.exact.Widget"


def test_cache_panel_pages_full_buffer() -> None:
    from hedron_core.cache.tracing import clear_cache_traces, record_cache_trace
    from hedron_core.cache.types import CacheEvent

    clear_cache_traces()
    for i in range(80):
        record_cache_trace(
            CacheEvent(kind="hit", key_fingerprint=f"k{i:02d}", scope="public", detail=str(i))
        )
    client = _client()
    html = client.get("/hedron-explorer/cache")
    assert html.status_code == 200
    assert HED_EXPLORER_0001 in html.text
    assert "rel='next'" in html.text or 'rel="next"' in html.text
    assert "k79" in html.text or "k29" in html.text
