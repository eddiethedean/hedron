"""Packet-shape and cross-surface evidence for the phase 0.63 cut."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

from scripts._gate_063 import EXPECTED_GATES, GATE, PACKET_FILES, REPORT, validate_packet


def test_phase063_packet_has_exact_gate_contract_and_required_verification() -> None:
    assert validate_packet() == []
    gate = tomllib.loads(GATE.read_text(encoding="utf-8"))
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert tuple(row["id"] for row in gate["evidence"]) == EXPECTED_GATES
    assert tuple(row["id"] for row in report["gates"]) == EXPECTED_GATES
    assert report["summary"] == {
        "total": 27,
        "planned": 0,
        "implemented": 0,
        "verified": 27,
        "deferred": 0,
        "release_ready": True,
    }


def test_phase063_packet_files_are_cross_referenced() -> None:
    root = Path(__file__).parents[2]
    for name in PACKET_FILES:
        assert (root / "docs/acceptance" / name).is_file(), name
    manifest = json.loads(
        (root / "docs/acceptance/component-parts-manifest-063.json").read_text(encoding="utf-8")
    )
    assert manifest["registry_derived"] is True
    assert manifest["handwritten_entries"] is False


def test_phase063_progressive_gates_are_implemented() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    states = {item["id"]: item["state"] for item in report["gates"]}
    assert all(states[gate] == "Verified" for gate in ("BUNDLE-063", "VISUAL-063", "INTEROP-063"))
    assert report["progressive_dispositions"] == []
