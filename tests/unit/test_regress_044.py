"""REGRESS-044: 0.42/0.43 fixtures remain valid after 0.44 attaches."""

from __future__ import annotations

from tests.unit._helpers_044 import make_app, reset_044

from hedron import Page, Text
from hedron_core.patches import PropertyPatch


def setup_function() -> None:
    reset_044()


def test_property_patch_is_not_view_patch() -> None:
    from hedron_core.updates import Patch

    assert PropertyPatch is not Patch


def test_unmodeled_refreshable_still_works() -> None:
    from fastapi.testclient import TestClient

    app = make_app()

    @app.refreshable
    def status():
        return Text("live")

    @app.page("/")
    def home():
        return Page(status(), title="Home")

    client = TestClient(app)
    assert "live" in client.get("/").text
    frag = client.get(
        status.path,
        headers={"HX-Request": "true", "HX-Target": status.dom_id},
    )
    assert frag.status_code == 200
    assert "live" in frag.text
    assert status.schema is None


def test_fragment_decorator_still_returns_function() -> None:
    app = make_app()
    region = app.region("legacy", description="legacy")

    @app.fragment("/legacy", region=region)
    def legacy():
        return Text("legacy")

    assert callable(legacy) and not isinstance(legacy, type)
    from hedron.handles import FragmentHandle

    assert not isinstance(legacy, FragmentHandle)
