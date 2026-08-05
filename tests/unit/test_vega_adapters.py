from hedron_charts.optional_adapters import VegaLiteAdapter, VegaTransformAdapter
from hedron_core.visualization import ChartAccessibility


def test_vega_adapters() -> None:
    acc = ChartAccessibility(title="t", description="d")
    out = VegaLiteAdapter().compile({"mark": "bar", "data": {"values": []}}, accessibility=acc)
    assert out.kind == "vega-lite"
    out2 = VegaTransformAdapter().compile(
        {"mark": "bar", "transform": [{"filter": "datum.x > 0"}]}, accessibility=acc
    )
    assert out2.metadata["server_transforms"]
