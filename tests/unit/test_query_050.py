"""QUERY-050 search/filter/pagination and 2000-component fixture."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
from tests.unit._helpers_050 import reset_050

from hedron_core.codes import HED_EXPLORER_0001
from hedron_core.registry import register_component, reset_registry_for_tests
from hedron_explorer.router import explorer_router


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
    assert isinstance(body, list)
    assert len(body) <= 200
    page = client.get("/hedron-explorer/api/components?limit=50&cursor=0")
    payload = page.json()
    assert payload["truncated"] is True
    assert payload["total"] == 2000
    assert payload["diagnostic"] == HED_EXPLORER_0001
    assert payload["next_cursor"] == "50"


def test_search_filter_sort() -> None:
    register_component(logical_id="demo.alpha", name="Alpha", module="demo", distribution="z")
    register_component(logical_id="demo.beta", name="Beta", module="demo", distribution="a")
    client = _client()
    found = client.get("/hedron-explorer/api/components?q=Alpha")
    names = [row["name"] for row in found.json()]
    assert names == ["Alpha"]
    sorted_rows = client.get("/hedron-explorer/api/components?sort=distribution")
    assert [row["name"] for row in sorted_rows.json()][0] == "Beta"
