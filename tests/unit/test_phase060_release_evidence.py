"""Packet-shape evidence for the phase 0.60 release gate."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

from scripts._gate_060 import EXPECTED_GATES, GATE, REPORT


def test_phase060_manifest_and_report_have_the_same_exact_27_gate_contract() -> None:
    manifest = tomllib.loads(GATE.read_text(encoding="utf-8"))
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    manifest_rows = manifest["evidence"]
    report_rows = report["gates"]

    assert tuple(row["id"] for row in manifest_rows) == EXPECTED_GATES
    assert tuple(row["id"] for row in report_rows) == EXPECTED_GATES
    assert report["summary"] == {
        "total": 27,
        "planned": 0,
        "implemented": 0,
        "verified": 27,
        "release_ready": True,
    }


def test_phase060_packet_files_are_cross_referenced() -> None:
    root = Path(__file__).parents[2]
    gate = tomllib.loads(GATE.read_text(encoding="utf-8"))
    for key in ("contract", "inventory", "tracking", "compatibility", "upgrade_fixture"):
        assert (GATE.parent / str(gate[key])).is_file()
    assert (root / "docs/implementation/EXECUTION_0_60.md").is_file()
