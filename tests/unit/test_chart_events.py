from hedron_charts.plugin import PLUGIN_META
from hedron_core.visualization import ChartEvent, validate_chart_event


def test_chart_event_kinds_and_plugin_version() -> None:
    for kind in ("hover", "click", "box", "lasso", "relayout", "restyle", "extend", "prepend"):
        validate_chart_event(ChartEvent(kind=kind, trace_id="t0", payload={}))
    assert "0.29" in PLUGIN_META.hedron_version
