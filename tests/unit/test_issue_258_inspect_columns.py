"""#258: inspect_data must raise HED-DATA-0005 on mismatched column lengths."""

from __future__ import annotations

import pytest

from hedron_core.auto import inspect_data
from hedron_core.diagnostics import HedronError


def test_mismatched_column_oriented_dict_raises() -> None:
    with pytest.raises(HedronError, match="HED-DATA-0005"):
        inspect_data({"a": [1, 2], "b": [10]})


def test_aligned_column_oriented_dict_inspects() -> None:
    report = inspect_data({"a": [1, 2], "b": [10, 20]})
    assert report.row_count == 2
    assert report.columns == ("a", "b")
