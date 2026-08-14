from __future__ import annotations

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from _gate_040 import (  # noqa: E402
    EXPECTED_GATES,
    FLEET_INVENTORY,
    GATE_TESTS,
    INVENTORY,
    MATRIX,
    MEDIUM_ISSUES,
    TRACKING_ISSUE,
    missing_refine_citations,
    rfc_resolved_questions_present,
)

EXPECTED_GATES_SET = {
    "AUTHOR-040",
    "PLUGIN-040",
    "HDJ-040",
    "THEME-040",
    "EXPLORER-040",
    "CONF-040",
    "MIGRATE-040",
    "SUPPLY-040",
    "REGRESS-040",
    "PKG-040",
}


def test_phase040_manifest_commands_exist() -> None:
    path = ROOT / "docs" / "acceptance" / "release-gate-0.40.toml"
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    rows = data["evidence"]
    assert {row["id"] for row in rows} == EXPECTED_GATES_SET
    assert {row["state"] for row in rows} == {"Verified"}
    assert set(GATE_TESTS) == EXPECTED_GATES_SET
    for gate_id, tests in GATE_TESTS.items():
        assert tests, gate_id
    for row in rows:
        command_path = ROOT / row["command"].removeprefix("python ")
        assert command_path.is_file(), row["command"]


def test_phase040_inventory_locks_author_and_island() -> None:
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    assert data["state"] == "verified"
    assert data["living_published_baseline"] == "v0.39.0"
    assert data["hedron_cut"] == "v0.40.0"
    assert data["owning_decision"] == "D-068"
    assert data["author_kit"]["private_apis"] is False
    assert data["author_kit"]["scaffold_command"] == "hedron new element"
    assert data["npm_mirror"]["react_runtime"] is False
    assert data["react_migration_matrix"]["island_in_hedron_elements"] is False


def test_phase040_fleet_inventory_baselines_039() -> None:
    data = tomllib.loads(FLEET_INVENTORY.read_text(encoding="utf-8"))
    assert data["baseline"] == "v0.39.0"
    assert data["state"] in {"planned", "verified"}
    assert "hedron_chart" in data["hedron-charts"]["supported"]
    assert data["hedron-elements"]["disposition"] == "incubator"


def test_phase040_decision_and_roadmap_agree() -> None:
    decisions = (ROOT / "docs" / "DECISIONS.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs" / "ROADMAP.md").read_text(encoding="utf-8")
    rfc = (ROOT / "docs" / "rfcs" / "RFC-0060-WEB-COMPONENT-PLATFORM.md").read_text(
        encoding="utf-8"
    )
    release = (ROOT / "docs" / "acceptance" / "RELEASE_0_40.md").read_text(encoding="utf-8")
    assert "| D-068 | Accepted |" in decisions
    assert "**Status:** Accepted" in rfc[:800]
    assert rfc_resolved_questions_present()
    assert TRACKING_ISSUE in release
    assert TRACKING_ISSUE in roadmap
    assert "## 0.40 — Web Component authoring and interoperability" in roadmap
    assert "Published as `v0.40.0`" in roadmap


def test_phase040_medium_issues_are_cited() -> None:
    assert MEDIUM_ISSUES == (162, 203, 204, 219, 220, 222)
    assert len(MEDIUM_ISSUES) == 6
    assert not missing_refine_citations()


def test_phase040_matrix_catalog_exists() -> None:
    text = MATRIX.read_text(encoding="utf-8")
    assert "ReactMigrationMatrix dispositions" in text
    assert "Island bridge (Experimental)" in text
    assert "Author kit surfaces" in text


def test_verified_gate_cannot_pass_without_executable_evidence(monkeypatch) -> None:
    import _gate_040

    monkeypatch.setattr(_gate_040, "gate_state", lambda _gate_id: "Verified")
    monkeypatch.setattr(_gate_040, "GATE_TESTS", {})
    assert _gate_040.check_gate("AUTHOR-040") == 1


def test_expected_gates_tuple_matches_manifest() -> None:
    assert set(EXPECTED_GATES) == EXPECTED_GATES_SET
    assert EXPECTED_GATES[-1] == "PKG-040"
