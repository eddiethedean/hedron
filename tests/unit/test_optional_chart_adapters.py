from hedron.testing import render_html
from hedron_charts.host_render import downsample_plotly_body, extract_folium_payload
from hedron_charts.optional_adapters import (
    ChartJsAdapter,
    EChartsAdapter,
    FoliumAdapter,
    GreatTablesAdapter,
    PlotlyResamplingAdapter,
    SigmaAdapter,
    ThreeJsAdapter,
    optional_adapters,
)
from hedron_core.visualization import ChartAccessibility


def test_optional_adapters_compile_and_host_markup() -> None:
    acc = ChartAccessibility(title="t", description="d")
    chartjs = ChartJsAdapter().compile({"type": "bar", "data": {}}, accessibility=acc)
    html = render_html(ChartJsAdapter().render_node(chartjs))
    assert "data-hedron-chart" in html
    assert "chartjs" in html
    assert "data-hedron-payload" in html

    echarts = EChartsAdapter().compile({"series": []}, accessibility=acc)
    assert "data-hedron-chart" in render_html(EChartsAdapter().render_node(echarts))

    GreatTablesAdapter().compile([{"a": 1}], accessibility=acc)
    SigmaAdapter().compile({"nodes": [{"id": "1"}], "edges": []}, accessibility=acc)
    ThreeJsAdapter().compile({"model_url": "model.glb", "bytes": 10}, accessibility=acc)

    resampled = PlotlyResamplingAdapter().compile(
        {
            "resample": True,
            "max_points": 10,
            "data": [{"x": list(range(5000)), "y": list(range(5000))}],
        },
        accessibility=acc,
    )
    body = resampled.body
    assert isinstance(body, str)
    import json

    parsed = json.loads(body)
    assert parsed["resampled"] is True
    assert len(parsed["data"][0]["x"]) <= 10

    assert len(optional_adapters()) >= 10


def test_folium_extracts_csp_safe_map_payload() -> None:
    acc = ChartAccessibility(title="map", description="m")
    out = FoliumAdapter().compile(
        {"type": "folium", "center": [37.7, -122.4], "zoom": 10, "markers": []},
        accessibility=acc,
    )
    html = render_html(FoliumAdapter().render_node(out))
    assert "maplibre" in html
    assert "data-hedron-payload" in html
    assert "<script" not in html.lower()
    payload = extract_folium_payload(
        {"type": "folium", "location": [1.0, 2.0], "zoom": 3, "markers": [{"location": [1, 2]}]}
    )
    assert payload["center"] == [1.0, 2.0]


def test_downsample_plotly_body() -> None:
    body = downsample_plotly_body(
        {"data": [{"x": list(range(100)), "y": list(range(100))}]},
        max_points=10,
    )
    assert len(body["data"][0]["x"]) <= 10
    assert body["resampled"] is True
