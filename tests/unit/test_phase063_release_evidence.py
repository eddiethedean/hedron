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
        "verified": 24,
        "deferred": 3,
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


def test_phase063_progressive_omissions_have_fallbacks() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    omissions = {item["gate"]: item for item in report["progressive_dispositions"]}
    assert omissions["BUNDLE-063"]["fallback"] == "complete stylesheet"
    assert omissions["VISUAL-063"]["fallback"] == "semantic/table visualization"
    assert omissions["INTEROP-063"]["fallback"] == "no React island"
