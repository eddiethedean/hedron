from hedron_charts.optional_adapters import (
    ChartJsAdapter,
    EChartsAdapter,
    GreatTablesAdapter,
    PlotlyResamplingAdapter,
    SigmaAdapter,
    ThreeJsAdapter,
    optional_adapters,
)
from hedron_core.visualization import ChartAccessibility


def test_optional_adapters_compile() -> None:
    acc = ChartAccessibility(title="t", description="d")
    ChartJsAdapter().compile({"type": "bar", "data": {}}, accessibility=acc)
    EChartsAdapter().compile({"series": []}, accessibility=acc)
    GreatTablesAdapter().compile([{"a": 1}], accessibility=acc)
    SigmaAdapter().compile({"nodes": [{"id": "1"}], "edges": []}, accessibility=acc)
    ThreeJsAdapter().compile({"model_url": "model.glb", "bytes": 10}, accessibility=acc)
    PlotlyResamplingAdapter().compile({"resample": True, "max_points": 100}, accessibility=acc)
    assert len(optional_adapters()) >= 10
