"""Edron Phase 0.9 implementation and Hedron 0.67.0 train contract."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_phase09_packet_is_implemented_on_hedron_067() -> None:
    packet = (ROOT / "docs/acceptance/EDRON_009.md").read_text(encoding="utf-8")
    gates = tomllib.loads((ROOT / "docs/acceptance/edron-phase09.toml").read_text(encoding="utf-8"))

    assert "edron==0.9.1" in packet
    assert "Hedron `0.67.0`" in packet
    assert gates["phase"] == "0.9"
    assert gates["status"] == "Implemented"
    assert gates["version"] == "0.9.1"
    assert gates["hedron_train"] == "0.67.0"
    assert gates["hedron_requirement"] == ">=0.67.0,<2.0"
    assert gates["hedron_lock_target"] == "hedron==0.67.0"
    assert gates["hedron_forward_compatibility_target"] == "1.0.0"
    assert gates["hedron_1_0_dependency_policy"] == "declare-after-release-candidate-verification"
    assert gates["deprecated_feature_policy"] == "warning-and-migration-input-only"
    assert "hedron-disclose direct tag/controller path" in gates["forbidden_compatibility_paths"]
    assert "EDR-09-CLEAN-067" in {row["id"] for row in gates["gate"]}
    assert all(row["state"] == "Implemented" for row in gates["gate"])


def test_phase09_uses_the_09_hedron_boundary() -> None:
    project = tomllib.loads((ROOT / "packages/edron/pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]
    roadmap = (ROOT / "docs/EDRON_ROADMAP.md").read_text(encoding="utf-8")

    assert project["version"] == "0.9.1"
    assert "hedron>=0.67.0,<2.0" in project["dependencies"]
    assert "hedron-data>=0.67.0,<2.0" in project["dependencies"]
    assert "Edron `0.8.x` remains pinned" in roadmap
    assert "Hedron `0.66.2` train" in roadmap
