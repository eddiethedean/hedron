"""REGRESS-043: 0.42 region facade and property patches remain distinct."""

from __future__ import annotations

from tests.unit._helpers_043 import make_app, reset_043

from hedron import Page, Text
from hedron_core.patches import PropertyPatch


def setup_function() -> None:
    reset_043()


def test_property_patch_module_is_not_view_patch() -> None:
    from hedron_core.updates import Patch

    assert PropertyPatch is not Patch
    assert PropertyPatch.__module__.endswith("patches")


def test_legacy_fragment_and_refreshable_can_coexist() -> None:
    app = make_app()
    region = app.region("box", description="box")

    @app.fragment("/box", region=region)
    def box():
        return Text("box")

    @app.refreshable
    def status():
        return Text("status")

    @app.page("/")
    def home():
        return Page(status(), title="Home")

    assert box.__name__ == "box"
    assert status.logical_id == "status"


def test_interaction_result_refresh_still_means_hx_refresh() -> None:
    from hedron_core.interaction import InteractionResult

    result = InteractionResult(content=None, refresh=True)
    assert result.refresh is True
