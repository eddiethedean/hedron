"""#359: hedron-map must keep compiled zoom 0."""

from __future__ import annotations

from hedron_maps import OpenStreetMap, compile_map
from hedron_maps.assets_047 import map_module_path
from hedron_maps.spec import AccessibilityDef, MapSpec, ViewState


def test_compile_accepts_zoom_zero() -> None:
    plan = compile_map(
        MapSpec(
            basemap=OpenStreetMap.standard(),
            view=ViewState(zoom=0),
            accessibility=AccessibilityDef(title="T", description="D"),
        )
    )
    assert plan.view.zoom == 0.0


def test_host_does_not_coalesce_zoom_zero_to_two() -> None:
    src = map_module_path().read_text(encoding="utf-8")
    assert "Number(view.zoom) || 2" not in src
    assert "Number.isFinite(zoom)" in src
