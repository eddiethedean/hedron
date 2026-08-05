from hedron_charts.pins import RUNTIME_PINS, ensure_pin_stubs, pinned_runtime, verify_pin


def test_runtime_pins() -> None:
    ensure_pin_stubs()
    assert "plotly" in RUNTIME_PINS
    meta = pinned_runtime("plotly-host")
    assert "digest" in meta
    from pathlib import Path

    host = (
        Path(__file__).resolve().parents[2]
        / "packages/hedron-charts/src/hedron_charts/assets/plotly/host.js"
    )
    assert verify_pin("plotly-host", host.read_bytes())
