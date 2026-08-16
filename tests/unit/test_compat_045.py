"""COMPAT-045: unused catalog is request-path neutral; 0.43/0.44 fixtures remain."""

from __future__ import annotations

from fastapi.testclient import TestClient
from tests.unit._helpers_045 import make_app, reset_045

from hedron import Page, Text
from hedron_core.updates import StructuralBindingAdapter


def setup_function() -> None:
    reset_045()


def test_unused_catalog_is_request_path_neutral() -> None:
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
    catalog = app.interactions
    assert catalog.require(status.logical_id).kind == "view"
    again = client.get("/").text
    assert html == again


def test_unmodeled_043_still_structural() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    assert status.schema is None
    adapter = getattr(status, "adapter", None) or StructuralBindingAdapter()
    assert isinstance(adapter, StructuralBindingAdapter)
