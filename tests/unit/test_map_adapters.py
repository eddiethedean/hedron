from hedron_charts.optional_adapters import GeospatialLayerAdapter, MapLibreAdapter, PyDeckAdapter
from hedron_core.visualization import ChartAccessibility


def test_map_adapters() -> None:
    acc = ChartAccessibility(title="t", description="d")
    assert (
        PyDeckAdapter().compile({"layers": []}, accessibility=acc).metadata["adapter"] == "pydeck"
    )
    assert MapLibreAdapter().compile({"style": "basic"}, accessibility=acc)
    assert GeospatialLayerAdapter().compile(
        {"type": "FeatureCollection", "features": []}, accessibility=acc
    )
