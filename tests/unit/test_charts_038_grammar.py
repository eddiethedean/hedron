"""GRAMMAR-038 / Stage 1 fixtures + ChartSpec compiler evidence."""

from __future__ import annotations

import pytest
from tests.unit.charts_038_helpers import sample_plan, sample_rows, sample_spec

from hedron_charts.compile import CANVAS_MARK_THRESHOLD, compile_chart, parse_chart_spec
from hedron_charts.operators import ALLOWED_OPERATORS, EVENT_KINDS
from hedron_charts.spec import SCHEMA_VERSION
from hedron_core.diagnostics import HedronError


def test_stage1_canvas_threshold_locked() -> None:
    assert CANVAS_MARK_THRESHOLD == 2500


def test_spec_roundtrip_fingerprint_stable() -> None:
    spec = sample_spec()
    plan_a = compile_chart(spec)
    plan_b = compile_chart(spec.to_json_dict())
    assert plan_a.spec_fingerprint == plan_b.spec_fingerprint
    assert plan_a.data_fingerprint == plan_b.data_fingerprint
    assert plan_a.schema_version == SCHEMA_VERSION


def test_unknown_field_fails_closed() -> None:
    raw = sample_spec().to_json_dict()
    raw["javascript"] = "alert(1)"
    with pytest.raises(HedronError) as ei:
        parse_chart_spec(raw)
    assert ei.value.diagnostic.code in {"HED-CHART-0021", "HED-CHART-0070", "HED-CHART-0022"}


def test_unknown_operator_fails() -> None:
    raw = sample_spec().to_json_dict()
    raw["transforms"] = [{"op": "eval", "field": "y"}]
    with pytest.raises(HedronError) as ei:
        compile_chart(raw)
    assert str(ei.value.diagnostic.code).startswith("HED-CHART-")


def test_unknown_schema_version_fails() -> None:
    raw = sample_spec().to_json_dict()
    raw["schema_version"] = 99
    with pytest.raises(HedronError) as ei:
        parse_chart_spec(raw)
    assert ei.value.diagnostic.code == "HED-CHART-0020"


def test_prototype_pollution_rejected() -> None:
    raw = sample_spec().to_json_dict()
    raw["composition"] = {"__proto__": {"x": 1}}
    with pytest.raises(HedronError) as ei:
        parse_chart_spec(raw)
    assert ei.value.diagnostic.code == "HED-CHART-0070"


def test_closed_operator_catalog_nonempty() -> None:
    assert "sum" in ALLOWED_OPERATORS
    assert "filter" in ALLOWED_OPERATORS
    assert "inspect" in EVENT_KINDS


def test_beginner_kinds_compile() -> None:
    for kind in ("line", "area", "bar", "scatter"):
        plan = sample_plan(kind=kind)
        assert plan.mark_count == len(sample_rows())
        assert plan.accessibility.title == "Sample"


def test_transform_filter_and_aggregate() -> None:
    raw = sample_spec().to_json_dict()
    raw["transforms"] = [
        {"op": "filter", "field": "y", "params": {"compare": "gt", "value": 2}},
        {
            "op": "aggregate",
            "params": {"groupby": [], "metrics": [{"op": "sum", "field": "y", "as": "total"}]},
        },
    ]
    plan = compile_chart(raw)
    assert plan.transformed_rows
    assert "total" in plan.transformed_rows[0]


def test_missing_and_empty_data() -> None:
    plan_missing = sample_plan(data=sample_rows("missing"))
    assert plan_missing.mark_count >= 1
    plan_empty = sample_plan(data=[])
    assert plan_empty.mark_count == 0
