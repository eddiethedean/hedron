"""Phase 0.16 analysis workbenches."""

from __future__ import annotations

import pytest

from hedron.testing import assert_renders, transform_plan_fixture
from hedron_core.testing.workbench import assert_transform_plan_bounded
from hedron_extras.workbench import (
    CallableActionForm,
    ChartWorkbench,
    CodeEditor,
    DataExplorer,
    JSONEditor,
)


def test_data_explorer_emits_plan_contract() -> None:
    html = assert_renders(
        DataExplorer(
            [{"field": "status", "label": "Status", "values": ["open", "closed"]}],
            max_rows=100,
            mark="explorer",
        ),
        contains='data-emits="transform-plan"',
    )
    assert 'data-collect-distributed="never"' in html
    plan = transform_plan_fixture(limit=100)
    assert_transform_plan_bounded(plan, max_rows=100)


def test_json_and_code_editors() -> None:
    assert_renders(JSONEditor({"a": 1}, schema={"type": "object"}), contains="hedron-json-editor")
    html = assert_renders(
        CodeEditor("print('hi')", language="python"),
        contains="hedron-code-editor",
    )
    assert 'data-no-eval="true"' in html
    assert 'data-csp-safe="true"' in html
    with pytest.raises(ValueError):
        CodeEditor("x", language="ruby")
    with pytest.raises(ValueError):
        CodeEditor("x" * 10, max_chars=5)
    with pytest.raises(ValueError, match="not valid JSON"):
        JSONEditor("{bad")


def test_chart_workbench_and_callable_form() -> None:
    chart = assert_renders(
        ChartWorkbench(title="Demo", chart="chart", table="table"),
        contains="hedron-chart-workbench",
    )
    assert 'method="post"' in chart
    html = assert_renders(
        CallableActionForm(
            "export_csv",
            [{"name": "limit", "label": "Limit", "kind": "int"}],
            form_action="/export",
        ),
        contains="hedron-callable-action-form",
    )
    assert 'data-implicit-exec="never"' in html
    assert 'action="/export"' in html
    with pytest.raises(ValueError):
        CallableActionForm("_private", [])
