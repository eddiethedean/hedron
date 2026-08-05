"""TEST-012: hedron.testing.data contract fixtures."""

from __future__ import annotations

import pytest

from hedron.testing.data import (
    assert_accessible_fallback,
    assert_budget,
    assert_stable_row_identity,
    assert_stable_trace_identity,
    chart_event_fixture,
    data_changes_fixture,
    data_query_fixture,
    grid_event_fixture,
    labeled_adversarial_cases,
    transform_plan_fixture,
)
from hedron_core.diagnostics import HedronError
from hedron_core.visualization import ChartEvent, validate_chart_event
from hedron_data.events import authorized_grid_event
from hedron_data.plans import apply_plan_in_memory


def test_query_and_changes_fixtures() -> None:
    q = data_query_fixture(limit=10)
    assert q.limit == 10
    changes = data_changes_fixture()
    assert changes.updates[0].row_key == "1"


def test_transform_plan_fixture_and_apply() -> None:
    plan = transform_plan_fixture()
    rows = apply_plan_in_memory(
        [{"value": 1, "name": "a"}, {"value": 2, "name": "b"}],
        plan,
    )
    assert rows and rows[0]["value"] == 1
    assert "steps" in plan.to_diagnostics()


def test_grid_and_chart_event_fixtures() -> None:
    grid = grid_event_fixture()
    authorized_grid_event(grid, allowed_fields=frozenset({"value"}), can_edit=True)
    with pytest.raises(HedronError):
        authorized_grid_event(grid, can_edit=False)
    chart = chart_event_fixture()
    assert_stable_trace_identity([chart])
    assert chart.accessible_fallback


def test_adversarial_cases_labeled() -> None:
    cases = labeled_adversarial_cases()
    assert any(c.kind == "adversarial" for c in cases)
    assert any(c.kind == "valid" for c in cases)
    with pytest.raises(HedronError):
        validate_chart_event(ChartEvent(kind="click", trace_id="t", payload={"blob": "x" * 80_000}))


def test_identity_and_budget_helpers() -> None:
    assert_stable_row_identity([{"id": "1"}, {"id": "2"}])
    assert_budget({"a": 1}, max_bytes=100)
    assert_accessible_fallback(description="ok")
