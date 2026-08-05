from hedron.testing import render_html
from hedron_charts.optional_adapters import (
    FoliumAdapter,
    GeospatialLayerAdapter,
    MapLibreAdapter,
    PyDeckAdapter,
)
from hedron_core.visualization import ChartAccessibility


def test_map_adapters() -> None:
    acc = ChartAccessibility(title="t", description="d")
    pydeck = PyDeckAdapter().compile({"layers": []}, accessibility=acc)
    assert pydeck.metadata["adapter"] == "pydeck"
    assert "data-hedron-chart" in render_html(PyDeckAdapter().render_node(pydeck))

    ml = MapLibreAdapter().compile(
        {"style": "basic", "center": [0, 0], "zoom": 1}, accessibility=acc
    )
    html = render_html(MapLibreAdapter().render_node(ml))
    assert "maplibre" in html
    assert "data-hedron-payload" in html

    geo = GeospatialLayerAdapter().compile(
        {"type": "FeatureCollection", "features": []}, accessibility=acc
    )
    assert "maplibre" in render_html(GeospatialLayerAdapter().render_node(geo))

    folium = FoliumAdapter().compile(
        {"type": "folium", "center": [40.0, -74.0], "zoom": 8, "markers": []},
        accessibility=acc,
    )
    folium_html = render_html(FoliumAdapter().render_node(folium))
    assert "maplibre" in folium_html
    assert "<script" not in folium_html.lower()
