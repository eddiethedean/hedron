"""hedron-charts: visualization adapters and chart components."""

from __future__ import annotations

from hedron_charts.adapters import AltairAdapter, MatplotlibAdapter, PlotlyAdapter, compile_figure
from hedron_charts.annotations import apply_annotations
from hedron_charts.components import (
    AltairChart,
    AreaChart,
    BarChart,
    LineChart,
    MatplotlibChart,
    PlotlyChart,
    ScatterChart,
)
from hedron_charts.optional_adapters import optional_adapters
from hedron_charts.pins import RUNTIME_PINS, ensure_pin_stubs, pinned_runtime, verify_pin

__version__ = "0.1.4"

__all__ = [
    "AltairAdapter",
    "AltairChart",
    "AreaChart",
    "BarChart",
    "LineChart",
    "MatplotlibAdapter",
    "MatplotlibChart",
    "PlotlyAdapter",
    "PlotlyChart",
    "RUNTIME_PINS",
    "ScatterChart",
    "__version__",
    "apply_annotations",
    "compile_figure",
    "ensure_pin_stubs",
    "optional_adapters",
    "pinned_runtime",
    "verify_pin",
]
