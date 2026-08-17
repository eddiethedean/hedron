"""WORKBENCH-046: Explorer/Jinja/CLI/notebook/sim consume bundles; no workflow store."""

from __future__ import annotations

from fastapi.testclient import TestClient
from tests.unit._helpers_046 import make_app, reset_046

from hedron import Page, Text
from hedron_core.bundles import FeatureBundle, included_bundles
from hedron_jinja import list_feature_bundles
from hedron_notebook import inspect_features as notebook_features
from hedron_sim import inspect_features as sim_features


def setup_function() -> None:
    reset_046()


def test_explorer_features_panel_and_cli_inspect() -> None:
    app = make_app(explorer="development")

    @app.refreshable
    def status():
        return Text("ok")

    app.include_feature(
        FeatureBundle(
            logical_id="tests:wb",
            provider="tests",
            provider_version="0.46.0",
            views=(status,),
            limitations=("reviewable",),
        )
    )

    @app.page("/")
    def home():
        return Page(status(), title="Home")

    html = TestClient(app).get("/hedron-explorer/features").text
    assert "tests:wb" in html
    assert "Feature bundles" in html
    assert "Skip to content" in html
    import argparse

    from hedron.cli.commands.inspect import _cmd_inspect_features
    from hedron.cli.parser import main

    ns = argparse.Namespace(json=True, app=None, component="features")
    assert _cmd_inspect_features(ns) == 0
    del main
    assert list_feature_bundles(app_id=app.hedron_app_id)[0].logical_id == "tests:wb"
    assert notebook_features(app_id=app.hedron_app_id)[0].logical_id == "tests:wb"
    assert sim_features(app_id=app.hedron_app_id)[0].logical_id == "tests:wb"
    assert included_bundles(app_id=app.hedron_app_id)[0].provider == "tests"
