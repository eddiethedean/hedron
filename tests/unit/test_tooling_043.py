"""TOOLING-043: Explorer graph, CLI checks, AppScenario, scaffold, HDJ."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from tests.unit._helpers_043 import make_app, reset_043

from hedron import Page, Text, refresh
from hedron.cli.commands.check import _check_043_handles
from hedron.cli.scaffold.fastapi import _scaffold_fastapi
from hedron_core.diagnostics import HedronError
from hedron_core.testing.adapters import fastapi_fixture
from hedron_core.testing.app import AppScenario
from hedron_core.updates import handle_graph_payload
from hedron_jinja.handles import resolve_registered_handle


def setup_function() -> None:
    reset_043()


def test_explorer_handle_graph_labels_dynamic_effects() -> None:
    app = make_app(explorer="development")

    @app.refreshable
    def status():
        return Text("ok")

    @app.command(fallback="/")
    def ping():
        return refresh(status)

    @app.page("/")
    def home():
        return Page(status(), title="Home")

    client = TestClient(app)
    graph = client.get("/hedron-explorer/graph")
    assert graph.status_code == 200
    assert "View / command graph" in graph.text
    assert "dynamic" in graph.text
    assert "declared" in graph.text
    payload = client.get("/hedron-explorer/api/handle-graph").json()
    assert payload["kind"] == "view-command-output"
    assert payload["effects"] == "dynamic/observed"
    kinds = {node["kind"] for node in payload["nodes"]}
    assert kinds == {"view", "command"}
    asset = client.get("/hedron-explorer/api/graph").json()
    assert "kind" not in asset or asset.get("kind") != "view-command-output"


def test_cli_handle_checks_and_scaffold(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text(
        """
from hedron import Hedron, refresh

app = Hedron(
    title="t",
    security="development",
    explorer="off",
    session_secret="secret-for-tests-32chars-ok!!",
)

@app.refreshable
def a():
    return "a"

@app.refreshable
def b():
    return "b"

@app.command
def nfb():
    return refresh(a)

@app.fragment("/old")
def old():
    return "old"
""",
        encoding="utf-8",
    )
    diags = _check_043_handles(tmp_path)
    codes = {d.code for d in diags}
    titles = [d.title for d in diags]
    assert "HED-CMD-0002" in codes
    assert any("migrat" in t.lower() for t in titles)
    ns = argparse.Namespace(name="demo")
    dest = tmp_path / "scaffold"
    dest.mkdir()
    assert _scaffold_fastapi(ns, dest) == 0
    source = (dest / "app.py").read_text(encoding="utf-8")
    assert '@app.view("/status")' in source
    assert "refresh_button" in source
    assert "ToastHost" in source
    assert "swap(" not in source
    assert "app.region" not in source
    assert "@app.fragment" not in source


def test_app_scenario_handle_api() -> None:
    app = make_app(security="standard")

    @app.refreshable
    def status():
        return Text("ready")

    @app.command(fallback="/")
    def ping():
        return refresh(status)

    @app.page("/")
    def home():
        return Page(status(), ping.button("Ping"), title="Home")

    fixture = fastapi_fixture(app)
    scenario = AppScenario.from_fixture(fixture)
    page = scenario.navigate("/")
    scenario.expect(status, contains="ready", response=page)
    refreshed = scenario.refresh(status)
    scenario.expect(status, contains="ready", response=refreshed)
    token = page.cookies.get("hedron_csrf") or scenario.cookies.get("hedron_csrf") or ""
    ran = scenario.run(ping, headers={"X-CSRF-Token": token})
    scenario.expect_refreshes(status, response=ran)


def test_hdj_requires_registered_handle() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    descriptor = resolve_registered_handle("status", app_id=app.hedron_app_id)
    assert descriptor.kind == "view"
    with pytest.raises(HedronError):
        resolve_registered_handle("/implicit/route")
    payload = handle_graph_payload(app_id=app.hedron_app_id)
    assert payload["kind"] == "view-command-output"
