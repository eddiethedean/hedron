"""Evidence-only: release-gate packet inventory for 0.43 (not product behavior)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from _gate_043 import (  # noqa: E402
    EXPECTED_GATES,
    GATE_TESTS,
    TRACKING_ISSUE,
    accepted_contract_present,
    cross_phase_refinement_present,
)
from tests.unit._packet_evidence import (  # noqa: E402
    assert_phase_packet_manifest,
    assert_phase_packet_tracking,
)


def test_phase043_manifest_commands_exist() -> None:
    assert_phase_packet_manifest(
        version="0.43",
        expected_gates=EXPECTED_GATES,
        gate_tests=GATE_TESTS,
        packet_test_relpath="tests/unit/test_phase043_packet.py",
    )


def test_phase043_tracking_and_contract() -> None:
    assert TRACKING_ISSUE == "#311"
    assert_phase_packet_tracking(
        version="0.43",
        tracking_issue=TRACKING_ISSUE,
        contract_checks=(accepted_contract_present, cross_phase_refinement_present),
    )
