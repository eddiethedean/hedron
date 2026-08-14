"""PERF-038 budgets and max_points remediation (#83)."""

from __future__ import annotations

import gzip

import pytest
from tests.unit.charts_038_helpers import sample_plan, sample_rows

from hedron_charts.assets_038 import chart_module_path
from hedron_charts.compile import CANVAS_MARK_THRESHOLD
from hedron_charts.host_render import downsample_plotly_body
from hedron_charts.optional_adapters import PlotlyResamplingAdapter
from hedron_core.diagnostics import HedronError
from hedron_core.visualization import ChartAccessibility


def test_core_bundle_gzip_budget() -> None:
    gz = gzip.compress(chart_module_path().read_bytes())
    assert len(gz) <= 90 * 1024


def test_dense_uses_canvas() -> None:
    plan = sample_plan(data=sample_rows("dense"))
    assert plan.renderer.paint == "canvas"
    assert plan.renderer.canvas_threshold == CANVAS_MARK_THRESHOLD


def test_negative_max_points_rejected() -> None:
    with pytest.raises(ValueError):
        downsample_plotly_body({"x": list(range(100)), "y": list(range(100))}, max_points=-5)


def test_plotly_resampling_adapter_rejects_nonpositive() -> None:
    adapter = PlotlyResamplingAdapter()
    acc = ChartAccessibility(title="t", description="d")
    with pytest.raises(HedronError) as ei:
        adapter.compile({"resample": True, "max_points": -1, "data": []}, accessibility=acc)
    assert ei.value.diagnostic.code == "HED-CHART-0002"
