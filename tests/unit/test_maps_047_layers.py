"""MAP-LAYER overlay grammar and SSR fallback."""

from __future__ import annotations

from hedron_core import RenderMode, render
from hedron_maps import (
    CircleLayer,
    GeoJSONLayer,
    LineLayer,
    Map,
    MarkerLayer,
    PolygonLayer,
    compile_map,
)
from hedron_maps.spec import AccessibilityDef, MapSpec, RasterLayer


def _acc() -> AccessibilityDef:
    return AccessibilityDef(title="Layers", description="Overlay test")


def test_typed_overlay_layers_compile() -> None:
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
                MarkerLayer(
                    markers=({"id": "a", "lat": 2.0, "lon": 1.0, "label": "A", "href": "/go"},)
                ),
                GeoJSONLayer(data=point),
                LineLayer(data=point),
                PolygonLayer(data=point),
                CircleLayer(data=point),
                RasterLayer(source="basemap"),
            ),
            accessibility=_acc(),
        )
    )
    kinds = [layer["kind"] for layer in plan.layers]
    assert kinds == ["marker", "geojson", "line", "polygon", "circle", "raster"]
    assert any(row["label"] == "A" for row in plan.accessibility.table_rows)


def test_ssr_wraps_core_alternative_table() -> None:
    html = render(
        Map(
            center=(0.0, 0.0),
            title="Markers",
            description="Table remains",
            markers=[{"id": "ferry", "lat": 37.79, "lon": -122.39, "label": "Ferry"}],
        ),
        mode=RenderMode.FRAGMENT,
    ).html
    assert "hedron-map-alternative" in html
    assert "Ferry" in html
    assert "hedron-map-fallback-figure" in html


def test_geojsonlayer_module_is_maps() -> None:
    assert GeoJSONLayer.__module__ == "hedron_maps.spec"
    from hedron_core.builtins.map_geo import GeoJSONLayer as CoreLayer

    assert CoreLayer.__module__.startswith("hedron_core")
    assert CoreLayer is not GeoJSONLayer
