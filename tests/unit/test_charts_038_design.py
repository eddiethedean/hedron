"""DESIGN-038 scales/layout/renderer decision evidence."""

from __future__ import annotations

import pytest
from tests.unit.charts_038_helpers import sample_plan, sample_rows, sample_spec

from hedron_charts.compile import CANVAS_MARK_THRESHOLD, compile_chart
from hedron_core.diagnostics import HedronError


def test_domains_inferred_with_zero_baseline_for_positive_bar() -> None:
    plan = sample_plan(kind="bar", data=sample_rows("categorical"))
    assert "y" in plan.domains or any(k.startswith("y") for k in plan.domains)
    y_domain = plan.domains.get("y") or next(iter(plan.domains.values()))
    assert y_domain[0] == 0


def test_log_scale_rejects_nonpositive() -> None:
    raw = sample_spec(data=[{"x": 1, "y": 0}, {"x": 2, "y": 2}]).to_json_dict()
    raw["scales"] = [{"name": "y", "type": "log"}]
    raw["marks"][0]["encodings"]["y"]["scale"] = "y"
    with pytest.raises(HedronError) as ei:
        compile_chart(raw)
    assert ei.value.diagnostic.code == "HED-CHART-0033"


def test_layout_density_modes() -> None:
    for density in ("compact", "ordinary", "wide"):
        raw = sample_spec().to_json_dict()
        raw["theme"] = {**raw.get("theme", {}), "density": density}
        plan = compile_chart(raw)
        assert plan.layout["density"] == density
        assert plan.layout["margin"] > 0


def test_canvas_decision_above_threshold() -> None:
    dense = sample_rows("dense")
    plan = sample_plan(data=dense)
    assert plan.mark_count >= CANVAS_MARK_THRESHOLD
    assert plan.renderer.paint == "canvas"
    assert "threshold" in plan.renderer.reason


def test_svg_default_under_threshold() -> None:
    plan = sample_plan()
    assert plan.renderer.paint == "svg"
    assert plan.renderer.canvas_threshold == CANVAS_MARK_THRESHOLD


def test_guides_present() -> None:
    plan = sample_plan()
    assert plan.guides
    assert any(g.kind in {"axis", "title"} for g in plan.guides)
