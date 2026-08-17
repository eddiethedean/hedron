"""COMPAT-046: unused include_feature is request-path identical to 0.45."""

from __future__ import annotations

from fastapi.testclient import TestClient
from tests.unit._helpers_046 import make_app, reset_046

from hedron import Page, Text


def setup_function() -> None:
    reset_046()


def test_unused_include_feature_is_request_path_neutral() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("live")

    @app.page("/")
    def home():
        return Page(status(), title="Home")

    client = TestClient(app)
    html = client.get("/").text
    assert "live" in html
    again = client.get("/").text
    assert html == again
    catalog = app.interactions
    assert catalog.require(status.logical_id).kind == "view"


def test_feature_provider_absent_from_hedron_facade() -> None:
    import hedron

    assert "FeatureBundle" not in hedron.__all__
    assert "FeatureProvider" not in hedron.__all__
    assert "DataWorkspace" not in hedron.__all__
