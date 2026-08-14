"""EXPORT-038 deterministic exports."""

from __future__ import annotations

import pytest
from tests.unit.charts_038_helpers import sample_plan

from hedron_charts.export import (
    assert_no_remote_urls,
    export_csv,
    export_json,
    export_svg,
    plan_export_bundle,
)
from hedron_core.diagnostics import HedronError


def test_exports_deterministic() -> None:
    plan = sample_plan()
    assert export_csv(plan) == export_csv(plan)
    assert export_json(plan) == export_json(plan)
    assert export_svg(plan) == export_svg(plan)
    assert "<svg" in export_svg(plan)
    assert "spec_fingerprint" in export_json(plan)


def test_unauthorized_export_fails() -> None:
    plan = sample_plan()
    with pytest.raises(HedronError) as ei:
        export_csv(plan, authorized=False)
    assert ei.value.diagnostic.code == "HED-CHART-0061"


def test_bundle_has_no_remote_urls() -> None:
    plan = sample_plan()
    bundle = plan_export_bundle(plan)
    assert_no_remote_urls(bundle)


def test_secret_fields_redacted_in_plan_rows() -> None:
    plan = sample_plan(data=[{"x": 1, "y": 2, "password": "secret"}])
    assert plan.transformed_rows[0]["password"] == "***"
