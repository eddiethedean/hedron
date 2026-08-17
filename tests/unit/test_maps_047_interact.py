"""INTERACT-047 MapInteraction."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel
from tests.unit._helpers_046 import csrf_headers, make_app

from hedron_core.bundles import FeatureConflictError
from hedron_core.cross_filter import MAP_VIEWPORT_TRIGGER
from hedron_maps import (
    FeatureSelected,
    Map,
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


def test_map_interaction_binds_command_path_on_map() -> None:
    from hedron_core import RenderMode, render

    app = make_app()

    @app.command("/pick-ids")
    def pick(body: FeatureSelected) -> str:
        return "ok"

    chart_map = Map(title="T", description="D")
    binding = MapInteraction(
        map=chart_map,
        event="feature-selected",
        payload=FeatureSelected,
        command=pick,
        name="pick-layer",
    )
    app.include_feature(binding)
    assert (
        chart_map._interaction_commands["feature-selected"] == "/maps/pick-layer/feature-selected"
    )
    html = render(chart_map, mode=RenderMode.FRAGMENT).html
    assert "/maps/pick-layer/feature-selected" in html
    src = Path("packages/hedron-maps/src/hedron_maps/static/hedron-map.mjs").read_text(
        encoding="utf-8"
    )
    assert "data-hedron-map-commands" in src
    assert "hedron_csrf" in src
    client = TestClient(app)
    headers = csrf_headers(client)
    posted = client.post(
        "/maps/pick-layer/feature-selected",
        json={"ids": ["a", "b"], "layer": "pins"},
        headers=headers,
    )
    assert posted.status_code < 500
