"""EXPLORER-040 element inspection and failure simulation."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
from tests.unit._helpers_043 import csrf_headers

from hedron import Hedron, Page, Text
from hedron_core.registry import register_element_definition, reset_registry_for_tests
from hedron_explorer.router import explorer_router


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(explorer_router(), prefix="/hedron-explorer")
    return TestClient(app)


def test_explorer_lists_and_details_elements() -> None:
    reset_registry_for_tests()
    register_element_definition(
        logical_id="demo:ext-probe",
        tag_name="ext-probe",
        abi_version=1,
        module_asset_id="demo:ext-probe.mjs",
        events=("ext-probe-change",),
        parts=("label",),
        fallback={"module_failure": "retain server content"},
        first_party=False,
    )
    client = _client()
    listing = client.get("/hedron-explorer/elements")
    assert listing.status_code == 200
    assert "ext-probe" in listing.text
    assert "Elements" in listing.text
    detail = client.get("/hedron-explorer/elements/demo:ext-probe")
    assert detail.status_code == 200
    assert "demo:ext-probe" in detail.text
    assert "label" in detail.text


def test_explorer_element_simulate_failure_modes() -> None:
    reset_registry_for_tests()
    register_element_definition(
        logical_id="demo:ext-probe",
        tag_name="ext-probe",
        abi_version=1,
        module_asset_id="demo:ext-probe.mjs",
        fallback={"module_failure": "retain server content", "js_off": "visible"},
        first_party=False,
    )
    app = Hedron(
        title="ex040",
        security="standard",
        explorer="development",
        session_secret="secret-for-tests-32chars-ok!!",
    )

    @app.page("/")
    def home():
        return Page(Text("home"), title="Home")

    with TestClient(app) as client:
        missing = client.post(
            "/hedron-explorer/api/element-simulate",
            json={"logical_id": "demo:ext-probe", "failure": "module"},
        )
        assert missing.status_code == 403
        response = client.post(
            "/hedron-explorer/api/element-simulate",
            json={"logical_id": "demo:ext-probe", "failure": "module"},
            headers=csrf_headers(client),
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["fallback"] == "retain server content"
