"""INTERACT-047 MapInteraction."""

from __future__ import annotations

import pytest
from pydantic import BaseModel
from tests.unit._helpers_046 import make_app

from hedron_core.bundles import FeatureConflictError
from hedron_core.cross_filter import MAP_VIEWPORT_TRIGGER
from hedron_maps import (
    FeatureSelected,
    MapInteraction,
    ViewportChanged,
)
from hedron_maps.interaction import SUPPORTED_EVENTS


def test_map_interaction_requires_action_handle() -> None:
    class Cmd:
        pass

    with pytest.raises(FeatureConflictError):
        MapInteraction(
            map=object(),
            event="feature-selected",
            payload=FeatureSelected,
            command=Cmd(),
        )


def test_unknown_event_rejected() -> None:
    app = make_app()

    class Body(BaseModel):
        ids: list[str] = []

    @app.command("/pick")
    def pick(body: Body) -> str:
        return "ok"

    with pytest.raises(FeatureConflictError):
        MapInteraction(map=object(), event="brush", payload=FeatureSelected, command=pick)


def test_viewport_stacks_on_map_viewport_trigger() -> None:
    assert MAP_VIEWPORT_TRIGGER == "map.viewport"
    app = make_app()

    @app.command("/view")
    def view(body: ViewportChanged) -> str:
        return "ok"

    binding = MapInteraction(
        map=object(),
        event="viewport-changed",
        payload=ViewportChanged,
        command=view,
    )
    bundle = binding.to_bundle()
    assert bundle.projections[0].data["viewport_trigger"] == MAP_VIEWPORT_TRIGGER
    assert bundle.projections[0].data["reuse_chart_interaction"] is False
    assert {
        "feature-selected",
        "feature-activated",
        "viewport-changed",
        "layer-visibility-changed",
        "map-loaded",
        "map-failed",
    } == SUPPORTED_EVENTS
    app.include_feature(binding)
    assert any(item.logical_id == bundle.logical_id for item in app.state.hedron_bundles.values())
