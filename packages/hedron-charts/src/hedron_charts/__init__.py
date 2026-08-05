"""hedron-charts: visualization adapters and chart components."""

from __future__ import annotations

from hedron_charts.adapters import AltairAdapter, MatplotlibAdapter, PlotlyAdapter, compile_figure
from hedron_charts.components import AltairChart, LineChart, MatplotlibChart, PlotlyChart

__version__ = "0.1.0"

__all__ = [
    "AltairAdapter",
    "AltairChart",
    "LineChart",
    "MatplotlibAdapter",
    "MatplotlibChart",
    "PlotlyAdapter",
    "PlotlyChart",
    "__version__",
    "compile_figure",
]
