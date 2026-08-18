"""#360: compiled overlay layers must appear in MapLibre style sources."""

from __future__ import annotations

from hedron_maps import GeoJSONLayer, MarkerLayer, compile_map
from hedron_maps.spec import AccessibilityDef, MapSpec


def test_marker_and_geojson_overlays_fold_into_style() -> None:
    point = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "P"},
                "geometry": {"type": "Point", "coordinates": [1.0, 2.0]},
            }
        ],
    }
    plan = compile_map(
        MapSpec(
            layers=(
                MarkerLayer(markers=({"id": "a", "lat": 2.0, "lon": 1.0, "label": "A"},)),
                GeoJSONLayer(data=point),
            ),
            accessibility=AccessibilityDef(title="T", description="D"),
        )
    )
    sources = plan.style["sources"]
    assert any(
        source.get("type") == "geojson" and (source.get("data") or {}).get("features")
        for source in sources.values()
        if isinstance(source, dict)
    )
    kinds = [layer["kind"] for layer in plan.layers]
    assert kinds == ["marker", "geojson"]
    assert any(layer.get("type") == "circle" for layer in plan.style["layers"])
