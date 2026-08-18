"""SECURITY-050 production opt-in, simulate allowlist, CSRF frozen."""

from __future__ import annotations

from typing import get_args

from fastapi.testclient import TestClient
from tests.unit._helpers_050 import csrf_headers, make_app, reset_050

from hedron import Page, Text
from hedron.app.explorer import ExplorerMode
from hedron_explorer.services.simulation import SIMULATE_KEYS


def setup_function() -> None:
    reset_050()


def test_explorer_modes_frozen() -> None:
    assert set(get_args(ExplorerMode)) == {"off", "development", "secured"}


def test_csrf_required_and_simulate_allowlist() -> None:
    assert {
        "route",
        "allow_mutations",
        "mode",
        "target",
        "boosted",
        "history_restore",
        "status",
    } == SIMULATE_KEYS
    app = make_app(security="standard", explorer="development")

    @app.page("/")
    def home():
        return Page(Text("hi"), title="T")

    with TestClient(app) as client:
        bare = client.post("/hedron-explorer/api/simulate", json={"route": "home"})
        assert bare.status_code == 403
        headers = csrf_headers(client)
        ok = client.post("/hedron-explorer/api/simulate", json={"route": "home"}, headers=headers)
        assert ok.status_code == 200


def test_catalog_presence_is_not_authority() -> None:
    app = make_app(security="standard", explorer="off")

    @app.page("/")
    def home():
        return Page(Text("hi"), title="T")

    with TestClient(app) as client:
        missing = client.get("/hedron-explorer/")
        assert missing.status_code in {404, 405, 403}
