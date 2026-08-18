"""LAB-050 bounded simulate lab and read-only package health."""

from __future__ import annotations

from fastapi.testclient import TestClient
from tests.unit._helpers_050 import csrf_headers, make_app, reset_050

from hedron import Page, Text
from hedron_explorer.services.health import package_health
from hedron_explorer.services.simulation import SIMULATE_KEYS


def setup_function() -> None:
    reset_050()


def test_simulate_keys_and_mutations_403() -> None:
    assert "allow_mutations" in SIMULATE_KEYS
    app = make_app(security="standard", explorer="development")

    @app.page("/")
    def home():
        return Page(Text("hi"), title="T")

    with TestClient(app) as client:
        headers = csrf_headers(client)
        denied = client.post(
            "/hedron-explorer/api/simulate",
            json={"route": "home", "allow_mutations": True},
            headers=headers,
        )
        assert denied.status_code == 403
        preview = client.get("/hedron-explorer/api/click-preview?route=home")
        assert preview.status_code == 200
        ok = client.post(
            "/hedron-explorer/api/simulate",
            json={"route": "home"},
            headers=headers,
        )
        assert ok.status_code == 200
        body = ok.json()
        assert "scenario" in body
        assert body["scenario"].get("redacted") is True or "route" in body["scenario"]


def test_package_health_is_not_doctor() -> None:
    health = package_health()
    assert health["read_only"] is True
    assert health["package_doctor"] is False
    assert "entry_points" in health
    assert "version_skew" in health
    assert "duplicate_registrations" in health
    assert "conformance_envelope" in health
