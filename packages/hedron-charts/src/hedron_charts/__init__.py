"""hedron-charts: visualization adapters and chart components."""

from __future__ import annotations

from hedron_charts.adapters import AltairAdapter, MatplotlibAdapter, PlotlyAdapter, compile_figure
from hedron_charts.annotations import apply_annotations
from hedron_charts.compile import beginner_to_spec, compile_chart, parse_chart_spec
from hedron_charts.components import (
    AltairChart,
    AreaChart,
    BarChart,
    Chart,
    LineChart,
    MatplotlibChart,
    PlotlyChart,
    ScatterChart,
)
from hedron_charts.element import TAG_NAME, chart_from_beginner
from hedron_charts.export import export_csv, export_json, export_svg, plan_export_bundle
from hedron_charts.interaction import ChartInteraction
from hedron_charts.optional_adapters import optional_adapters
from hedron_charts.pins import RUNTIME_PINS, ensure_pin_stubs, pinned_runtime, verify_pin
from hedron_charts.spec import ChartPlan, ChartSpec

__version__ = "1.0.5"

__all__ = [
    "AltairAdapter",
    "AltairChart",
    "AreaChart",
    "BarChart",
    "Chart",
    "ChartInteraction",
    "ChartPlan",
    "ChartSpec",
    "LineChart",
    "MatplotlibAdapter",
    "MatplotlibChart",
    "PlotlyAdapter",
    "PlotlyChart",
    "RUNTIME_PINS",
    "ScatterChart",
    "TAG_NAME",
    "__version__",
    "apply_annotations",
    "beginner_to_spec",
    "chart_from_beginner",
    "compile_chart",
    "compile_figure",
    "ensure_pin_stubs",
    "export_csv",
    "export_json",
    "export_svg",
    "optional_adapters",
    "parse_chart_spec",
    "pinned_runtime",
    "plan_export_bundle",
    "verify_pin",
]
