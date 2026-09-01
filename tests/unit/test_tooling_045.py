"""TOOLING-045: Explorer, CLI, OpenAPI fingerprints, AppScenario catalog lookup."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from tests.unit._helpers_045 import make_app, reset_045

from hedron import Page, Text
from hedron.cli.commands.inspect import _cmd_inspect_interactions
from hedron.interactions import inspect_interactions_static
from hedron_core.testing.adapters import fastapi_fixture
from hedron_core.testing.app import AppScenario


def setup_function() -> None:
    reset_045()


def test_explorer_catalog_panel() -> None:
    app = make_app(explorer="development")

    @app.view("/status", include_in_schema=True)
    def status():
        return Text("ok")

    @app.page("/")
    def home():
        return Page(status(), title="Home")

    client = TestClient(app)
    page = client.get("/hedron-explorer/interactions")
    assert page.status_code == 200
    assert status.logical_id in page.text
    payload = client.get("/hedron-explorer/api/interactions")
    assert payload.status_code == 200
    body = payload.json()
    assert any(entry["logical_id"] == status.logical_id for entry in body["entries"])


def test_openapi_fingerprint_extensions() -> None:
    app = make_app()

    @app.view("/status", include_in_schema=True)
    def status():
        return Text("ok")

    expected = app.interactions.require(status.logical_id).descriptor_fingerprint
    app.state.hedron_interactions = app.interactions
    app.openapi_schema = None
    schema = app.openapi()
    fingerprints = []
    for path_item in schema.get("paths", {}).values():
        if not isinstance(path_item, dict):
            continue
        for operation in path_item.values():
            if isinstance(operation, dict) and operation.get("x-hedron-descriptor-fingerprint"):
                fingerprints.append(operation["x-hedron-descriptor-fingerprint"])
    assert expected in fingerprints


def test_static_cli_does_not_import_target(tmp_path: Path) -> None:
    source = tmp_path / "app.py"
    source.write_text(
        "from hedron import Hedron, Text\n"
        "app = Hedron(title='x')\n"
        "@app.view\n"
        "def card():\n"
        "    return Text('card')\n",
        encoding="utf-8",
    )
    payload = inspect_interactions_static(tmp_path)
    assert payload["unknown"] is True
    assert payload["provenance"]["mode"] == "static-source"
    assert any(entry["logical_id"] == "card" for entry in payload["entries"])
    assert any(entry["descriptor_fingerprint"] == "unknown" for entry in payload["entries"])


def test_json_inspect_interactions() -> None:
    app = make_app()

    @app.view
    def status():
        return Text("ok")

    class Args:
        json = True
        app = None
        manifest = None
        static = None
        component = "interactions"

    code = _cmd_inspect_interactions(Args())
    assert code == 0


def test_app_scenario_catalog_lookup() -> None:
    app = make_app()

    @app.view
    def status():
        return Text("ok")

    @app.page("/")
    def home():
        return Page(status(), title="Home")

    scenario = AppScenario.from_fixture(fastapi_fixture(app))
    entry = scenario.assert_catalog_kind(status.logical_id, "view", app_id=app.hedron_app_id)
    assert entry.descriptor_fingerprint
