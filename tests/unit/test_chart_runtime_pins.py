from pathlib import Path

from hedron_charts.pins import (
    RUNTIME_PINS,
    assert_pins_present,
    pinned_runtime,
    verify_pin,
)

_ASSETS = Path(__file__).resolve().parents[2] / "packages/hedron-charts/src/hedron_charts/assets"


def test_runtime_pins_are_real_bundles() -> None:
    assert_pins_present()
    assert "plotly" in RUNTIME_PINS
    plotly = _ASSETS / "plotly" / "plotly.min.js"
    body = plotly.read_bytes()
    assert len(body) > 100_000
    assert b"pin stub" not in body[:200]
    assert b"plotly.js" in body[:200] or b"Plotly" in body[:500]
    assert verify_pin("plotly", body)

    vega = (_ASSETS / "vega" / "vega.min.js").read_bytes()
    assert len(vega) > 50_000
    assert verify_pin("vega", vega)

    chartjs = (_ASSETS / "chartjs" / "chart.umd.min.js").read_bytes()
    assert len(chartjs) > 50_000
    assert verify_pin("chartjs", chartjs)

    host = _ASSETS / "plotly" / "host.js"
    meta = pinned_runtime("plotly-host")
    assert "digest" in meta
    assert verify_pin("plotly-host", host.read_bytes())
