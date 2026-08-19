"""WORKBENCH-051 cancel, revision, no-eval JSON."""

from __future__ import annotations

import pytest

from hedron.testing import assert_renders
from hedron_extras.workbench import ChartWorkbench, DataExplorer, JSONEditor


def test_json_editor_never_eval_and_cancel() -> None:
    html = assert_renders(
        JSONEditor({"a": 1}, revision="7"),
        contains='data-no-eval="true"',
    )
    assert "eval(" not in html
    assert 'name="json__cancel"' in html
    assert 'name="json__revision"' in html
    assert 'value="7"' in html
    with pytest.raises(ValueError, match="not valid JSON"):
        JSONEditor("{not json")
    with pytest.raises(ValueError, match="max_chars"):
        JSONEditor("{" + "a" * 10, max_chars=5)


def test_data_and_chart_apply_cancel_export() -> None:
    html = assert_renders(
        DataExplorer(
            [{"field": "status", "label": "Status", "values": ["open"]}],
            max_rows=10,
            revision="3",
        ),
        contains="__cancel",
    )
    assert "__apply" in html
    assert "__export" in html
    assert 'data-revision="3"' in html
    chart = assert_renders(ChartWorkbench(), contains="Export CSV")
    assert "__cancel" in chart
