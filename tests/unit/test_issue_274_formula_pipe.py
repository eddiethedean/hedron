"""#274: spreadsheet formula_policy must reject pipe DDE prefixes."""

from __future__ import annotations

import pytest

from hedron_core.diagnostics import HedronError
from hedron_data.spreadsheet import _reject_or_sanitize


def test_pipe_formula_prefix_is_rejected() -> None:
    with pytest.raises(HedronError) as caught:
        _reject_or_sanitize("|cmd /c calc", formula_policy="reject")
    assert caught.value.diagnostics[0].code == "HED-DATA-0040"


def test_pipe_formula_prefix_is_sanitized() -> None:
    assert _reject_or_sanitize("|cmd /c calc", formula_policy="sanitize") == "'|cmd /c calc"
