"""Phase 0.20 HTMX-020: profile-driven browser HTMX presets."""

from __future__ import annotations

from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from hedron import Hedron, Page, Text
from hedron.security.policy import SecurityPolicy
from hedron_core import reset_registry_for_tests


@pytest.fixture(autouse=True)
def _fresh_registry() -> None:
    reset_registry_for_tests()
    import hedron_core

    hedron_core._register_builtins()  # type: ignore[attr-defined]
    yield


def test_standard_preset_disables_history_cache() -> None:
    app = Hedron(title="demo", security="standard", explorer="off", session_secret="test-secret")

    @app.page("/")
    def home() -> Page:
        return Page(Text("home"), title="Home")

    client = TestClient(app)
    body = client.get("/").text
    assert 'name="htmx-config"' in body
    assert '"allowEval":false' in body
    assert '"allowScriptTags":false' in body
    assert '"historyEnabled":false' in body
    assert '"historyCacheSize":0' in body


def test_development_preset_keeps_history_enabled() -> None:
    app = Hedron(title="demo", security="development", explorer="off", session_secret="test-secret")

    @app.page("/")
    def home() -> Page:
        return Page(Text("home"), title="Home")

    client = TestClient(app)
    body = client.get("/").text
    assert '"allowEval":false' in body
    assert '"historyEnabled":false' not in body
    assert '"historyCacheSize":0' not in body


def test_htmx_browser_preset_opt_out_skips_meta() -> None:
    policy = replace(
        SecurityPolicy.from_name("standard"), htmx_browser_preset=False, explorer_enabled=False
    )
    app = Hedron(title="demo", security=policy, explorer="off", session_secret="test-secret")

    @app.page("/")
    def home() -> Page:
        return Page(Text("home"), title="Home")

    client = TestClient(app)
    body = client.get("/").text
    assert 'name="htmx-config"' not in body
    assert "htmx.min.js" in body


def test_policy_htmx_config_json_inspectable() -> None:
    standard = SecurityPolicy.from_name("standard").htmx_config_json()
    assert '"historyEnabled":false' in standard
    development = SecurityPolicy.from_name("development").htmx_config_json()
    assert '"historyEnabled":false' not in development
