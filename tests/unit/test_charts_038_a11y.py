"""A11Y-038 accessibility plan + tabular fallback remediation (#82)."""

from __future__ import annotations

from tests.unit.charts_038_helpers import sample_plan, sample_rows

from hedron_charts.adapters import _fallback_table
from hedron_charts.element import fallback_nodes
from hedron_core.html import html
from hedron_core.rendering import render


def test_accessibility_plan_fields() -> None:
    plan = sample_plan()
    assert plan.accessibility.title
    assert plan.accessibility.description
    assert plan.accessibility.encoding_explanation
    assert plan.accessibility.summary
    assert plan.accessibility.interaction_help
    assert plan.accessibility.include_table is True
    assert len(plan.accessibility.table_rows) == len(sample_rows())


def test_fallback_table_retains_all_admitted_rows() -> None:
    rows = [{"a": i, "b": i * 2} for i in range(80)]
    node = _fallback_table(rows)
    html_out = render(html.div(node)).html
    # Previously capped at 50; must retain >50 rows when under max_rows.
    assert html_out.count("<tr>") >= 81  # header + 80 body


def test_fallback_nodes_include_summary_and_table() -> None:
    plan = sample_plan()
    nodes = fallback_nodes(plan)
    assert len(nodes) >= 3
