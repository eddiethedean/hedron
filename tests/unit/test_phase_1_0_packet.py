"""Planning-honesty checks for the Hedron 1.0 Stage 0 packet."""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _toml(relative: str) -> dict[str, object]:
    return tomllib.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_phase_1_0_plan_checker_passes_without_verifying_release() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_100.py", "--check-plan"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "release gates remain Planned" in result.stdout


def test_phase_1_0_release_verification_fails_closed() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_100.py", "--gate", "ENTRY-100", "--verify"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert "ENTRY-100 is Planned" in result.stderr


def test_phase_1_0_gate_is_subtractive_and_planned() -> None:
    gate = _toml("docs/acceptance/release-gate-1.0.toml")
    contract = _toml("docs/acceptance/one-zero-cut-contract.toml")
    assert gate["phase"] == "1.0"
    assert gate["target"] == "v1.0.0"
    assert gate["status"] == "Planned"
    assert gate["stage_1_entry_satisfied"] is False
    assert all(row["state"] == "Planned" for row in gate["evidence"])
    assert contract["release_boundary"]["net_new_required_runtime_capabilities"] == 0
    assert contract["release_boundary"]["compatibility_layer_in_1_0"] is False
    assert contract["changes_runtime"] is False
    assert contract["changes_versions"] is False


def test_phase_1_0_keeps_verified_067_as_immutable_predecessor() -> None:
    predecessor = _toml("docs/acceptance/release-gate-0.67.toml")
    workspace = _toml("pyproject.toml")
    assert predecessor["status"] == "Verified"
    assert predecessor["target"] == "v0.67.0"
    assert workspace["project"]["version"] == "0.67.0"


def test_phase_1_0_packet_names_known_warning_floor_without_claiming_completeness() -> None:
    upgrade = (ROOT / "docs/acceptance/upgrade-fixtures-1.0.md").read_text(encoding="utf-8")
    contract = _toml("docs/acceptance/one-zero-cut-contract.toml")
    for spelling in ("app.component", "app.fragment", "app.include_feature"):
        assert spelling in upgrade
    gap = contract["migration"]["known_stage_0_gap"]
    assert "four" in gap
    assert "before any removal" in gap


def test_phase_1_0_execution_plan_is_actionable_and_complete() -> None:
    plan = (ROOT / "docs/implementation/HEDRON_1_0.md").read_text(encoding="utf-8")
    for heading in (
        "### W0 — inventory, baseline, and entry lock",
        "### W1 — canonical surface and type boundary",
        "### W2 — warning-backed removal slices",
        "### W3 — static checking and migration tooling",
        "### W4 — interaction and lifecycle cutover",
        "### W5 — component-engine cutover",
        "### W6 — consumer and documentation migration",
        "### W7 — quality closure after removals",
        "### W8 — dual-version and fleet compatibility",
        "### W9 — artifacts, release candidate, and cut",
        "## Pull-request sequence and ownership",
        "## Verification command matrix",
        "## Definition of done",
    ):
        assert heading in plan
    for artifact in (
        "public-inventory-100.toml",
        "stable-inventory-100.toml",
        "removal-inventory-100.toml",
        "warnings-100.toml",
        "baseline-100.json",
        "support-policy-100.md",
    ):
        assert artifact in plan
