"""REGRESS-046: 0.43/0.44/0.45 request paths remain after FeatureBundle attach."""

from __future__ import annotations

from fastapi.testclient import TestClient
from tests.unit._helpers_046 import make_app, reset_046

from hedron import Page, Text
from hedron_core.patches import PropertyPatch


def setup_function() -> None:
    reset_046()


def test_property_patch_is_not_view_patch() -> None:
    from hedron_core.updates import Patch

    assert PropertyPatch is not Patch


def test_unmodeled_refreshable_still_works_with_bundles() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("live")

    @app.page("/")
    def home():
        return Page(status(), title="Home")

    _ = app.interactions.require(status.logical_id)
    client = TestClient(app)
    assert "live" in client.get("/").text
    frag = client.get(
        status.path,
        headers={"HX-Request": "true", "HX-Target": status.dom_id},
    )
    assert frag.status_code == 200
