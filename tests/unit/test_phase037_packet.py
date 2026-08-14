from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from _gate_037 import (  # noqa: E402
    EXPECTED_GATES,
    HIGH_SEVERITY_ISSUES,
    missing_high_severity_citations,
)


def test_phase037_high_severity_issues_are_cited() -> None:
    assert HIGH_SEVERITY_ISSUES == (230, 231, 232, 233, 234, 235, 236, 237)
    assert not missing_high_severity_citations()


def test_phase037_gate_ids_remain_nine_rows() -> None:
    assert EXPECTED_GATES[-1] == "PKG-037"
    assert "REGRESS-037" in EXPECTED_GATES
    assert len(EXPECTED_GATES) == 9
