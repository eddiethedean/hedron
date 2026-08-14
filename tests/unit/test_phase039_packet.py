from __future__ import annotations

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from _gate_039 import (  # noqa: E402
    EXPECTED_GATES,
    FLEET_INVENTORY,
    GATE_TESTS,
    INVENTORY,
    MEDIUM_ISSUES,
    RICH_SURFACE,
    TRACKING_ISSUE,
    missing_refine_citations,
    rfc_resolved_questions_present,
)

EXPECTED_GATES_SET = {
    "DATA-039",
    "OPTIMISTIC-039",
    "CHARTLINK-039",
    "RICH-039",
    "WORKER-039",
    "PERF-039",
    "A11Y-039",
    "REGRESS-039",
    "PKG-039",
}


def test_phase039_manifest_commands_exist() -> None:
    path = ROOT / "docs" / "acceptance" / "release-gate-0.39.toml"
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    rows = data["evidence"]
    assert {row["id"] for row in rows} == EXPECTED_GATES_SET
    assert {row["state"] for row in rows} <= {"Planned", "Implemented", "Verified"}
    assert set(GATE_TESTS) == EXPECTED_GATES_SET
    for gate_id, tests in GATE_TESTS.items():
        assert tests, gate_id
    for row in rows:
        command_path = ROOT / row["command"].removeprefix("python ")
        assert command_path.is_file(), row["command"]


def test_phase039_inventory_locks_optimistic_and_chartlink() -> None:
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    assert data["state"] in {"planned", "verified"}
    assert data["living_published_baseline"] == "v0.38.0"
    assert data["hedron_cut"] == "v0.39.0"
    assert data["owning_decision"] == "D-067"
    assert "DataEditor" in data["optimistic"]["first_inventory"]
    assert data["chartlink"]["parallel_renderer"] is False
    assert data["regress"]["medium_low_issues"] == 27


def test_phase039_fleet_inventory_baselines_038() -> None:
    data = tomllib.loads(FLEET_INVENTORY.read_text(encoding="utf-8"))
    assert data["baseline"] == "v0.38.0"
    assert data["state"] in {"planned", "verified"}
    assert "hedron_chart" in data["hedron-charts"]["supported"]
    assert data["hedron-elements"]["disposition"] == "incubator"


def test_phase039_decision_and_roadmap_agree() -> None:
    decisions = (ROOT / "docs" / "DECISIONS.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs" / "ROADMAP.md").read_text(encoding="utf-8")
    rfc = (ROOT / "docs" / "rfcs" / "RFC-0060-WEB-COMPONENT-PLATFORM.md").read_text(
        encoding="utf-8"
    )
    release = (ROOT / "docs" / "acceptance" / "RELEASE_0_39.md").read_text(encoding="utf-8")
    assert "| D-067 | Accepted |" in decisions
    assert "**Status:** Accepted" in rfc[:800]
    assert rfc_resolved_questions_present()
    assert TRACKING_ISSUE in release
    assert TRACKING_ISSUE in roadmap
    assert "## 0.39 — Rich data and visualization elements" in roadmap
    assert "Stage 0 contract refined against Published `v0.38.0`" in roadmap or "Stage 0" in roadmap


def test_phase039_medium_issues_are_cited() -> None:
    assert MEDIUM_ISSUES == (
        73,
        84,
        102,
        104,
        105,
        107,
        113,
        115,
        116,
        117,
        118,
        119,
        120,
        121,
        176,
        188,
        189,
        190,
        191,
        192,
        193,
        194,
        221,
        240,
        241,
        247,
        248,
    )
    assert len(MEDIUM_ISSUES) == 27
    assert not missing_refine_citations()


def test_phase039_rich_surface_catalog_exists() -> None:
    text = RICH_SURFACE.read_text(encoding="utf-8")
    assert "OptimisticMutation first inventory" in text
    assert "Experimental exception policy" in text
    assert "Chart link" in text


def test_verified_gate_cannot_pass_without_executable_evidence(monkeypatch) -> None:
    import _gate_039

    monkeypatch.setattr(_gate_039, "gate_state", lambda _gate_id: "Verified")
    monkeypatch.setattr(_gate_039, "GATE_TESTS", {})
    assert _gate_039.check_gate("DATA-039") == 1


def test_expected_gates_tuple_matches_manifest() -> None:
    assert set(EXPECTED_GATES) == EXPECTED_GATES_SET
    assert EXPECTED_GATES[-1] == "PKG-039"
