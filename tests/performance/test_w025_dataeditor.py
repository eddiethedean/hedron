"""BUDGET-025 / W-025-DATAEDITOR — DataEditor row-model smoke soft budget."""

from __future__ import annotations

import time

import pytest

from hedron_core import render
from hedron_data import Column, DataEditor, DataQuery, InMemoryDataSource

pytestmark = pytest.mark.performance

_ROWS = 80
_EDITOR_MS = 1000


def test_w025_dataeditor_row_model_smoke() -> None:
    rows = [{"id": str(i), "name": f"user-{i}", "role": "member"} for i in range(_ROWS)]
    source = InMemoryDataSource(
        rows,
        writable_fields=frozenset({"name", "role"}),
        schema=(
            Column(name="id", read_only=True).to_schema(),
            Column(name="name").to_schema(),
            Column(name="role").to_schema(),
        ),
        version="1",
    )
    editor = DataEditor(
        source=source,
        columns=[
            Column(name="id", read_only=True),
            Column(name="name"),
            Column(name="role"),
        ],
        key_field="id",
    )

    t0 = time.perf_counter()
    page = source.fetch(DataQuery(limit=_ROWS))
    html = render(editor).html
    elapsed_ms = (time.perf_counter() - t0) * 1000

    assert elapsed_ms <= _EDITOR_MS
    assert page.total == _ROWS
    assert "hedron-data-editor" in html
    assert "user-0" in html
