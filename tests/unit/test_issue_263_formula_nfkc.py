"""#263: spreadsheet formula_policy must NFKC-fold lookalike prefixes."""

from __future__ import annotations

import pytest

from hedron_core.diagnostics import HedronError
from hedron_data.spreadsheet import _reject_or_sanitize


@pytest.mark.parametrize(
    "payload",
    [
        "﹦CMD()",
        "﹢1",
        "⁼1+1",
        "﹫cmd",
    ],
)
def test_nfkc_lookalike_prefixes_are_rejected(payload: str) -> None:
    with pytest.raises(HedronError, match="HED-DATA-0040"):
        _reject_or_sanitize(payload, formula_policy="reject")
    assert _reject_or_sanitize(payload, formula_policy="sanitize").startswith("'")
