from __future__ import annotations

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from _gate_042 import (  # noqa: E402
    EXPECTED_GATES,
    FLEET_INVENTORY,
    GATE_TESTS,
    INVENTORY,
    MEDIUM_ISSUES,
    TRACKING_ISSUE,
    living_published_baseline,
    missing_refine_citations,
    rfc_resolved_questions_present,
)

EXPECTED_GATES_SET = {
    "STABLE-042",
    "COMPAT-042",
    "REVIEW-042",
    "AT-042",
    "PERF-042",
    "SUPPLY-042",
    "REGRESS-042",
    "PKG-042",
}

LOCKED_TAGS = (
    "hedron-example",
    "hedron-field-text",
    "hedron-field-choice",
    "hedron-field-file",
    "hedron-disclosure",
    "hedron-dialog",
    "hedron-action-async",
    "hedron-data-editor",
)


def test_phase042_manifest_commands_exist() -> None:
    path = ROOT / "docs" / "acceptance" / "release-gate-0.42.toml"
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    rows = data["evidence"]
    assert {row["id"] for row in rows} == EXPECTED_GATES_SET
    assert {row["state"] for row in rows} == {"Planned"}
    assert set(GATE_TESTS) == EXPECTED_GATES_SET
    for gate_id, tests in GATE_TESTS.items():
        assert tests == ["tests/unit/test_phase042_packet.py"], gate_id
    for row in rows:
        command_path = ROOT / row["command"].removeprefix("python ")
        assert command_path.is_file(), row["command"]


def test_phase042_inventory_locks_supported_tags() -> None:
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    assert data["state"] == "planned"
    assert data["living_published_baseline"] == "v0.41.0"
    assert data["hedron_cut"] == "v0.42.0"
    assert data["owning_decision"] == "D-070"
    assert tuple(data["supported_tags"]) == LOCKED_TAGS
    assert data["npm_mirror"]["react_runtime"] is False
    assert data["react_migration_bridge"]["in_hedron_elements"] is False
    assert data["react_migration_bridge"]["disposition"] == "experimental"
    assert len(data["remediations"]["issues"]) == 32


def test_phase042_fleet_inventory_baselines_041() -> None:
    data = tomllib.loads(FLEET_INVENTORY.read_text(encoding="utf-8"))
    assert data["baseline"] == "v0.41.0"
    assert data["state"] == "planned"
    assert data["hedron_cut"] == "v0.42.0"
    assert "hedron_chart" in data["hedron-charts"]["supported"]
    elements = data["hedron-elements"]
    assert elements["disposition"] == "incubator"
    assert elements["maturity"] == "alpha"
    assert elements["pin"] == ">=0.41.0,<0.42"
    assert elements["supported"] == []
    assert "production_grade_until_0_42" in elements["excluded"]


def test_phase042_living_tip_unchanged() -> None:
    assert living_published_baseline() == "v0.41.0"
    release = tomllib.loads((ROOT / "docs" / "release.toml").read_text(encoding="utf-8"))
    assert release["release"]["published_version"] == "0.41.0"
    assert release["release"]["train"] == "0.41"
    workspace = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert workspace["project"]["version"].startswith("0.41.")


def test_phase042_decision_and_roadmap_agree() -> None:
    decisions = (ROOT / "docs" / "DECISIONS.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs" / "ROADMAP.md").read_text(encoding="utf-8")
    rfc = (ROOT / "docs" / "rfcs" / "RFC-0060-WEB-COMPONENT-PLATFORM.md").read_text(
        encoding="utf-8"
    )
    release = (ROOT / "docs" / "acceptance" / "RELEASE_0_42.md").read_text(encoding="utf-8")
    assert "| D-070 | Accepted |" in decisions
    assert "**Status:** Accepted" in rfc[:800]
    assert rfc_resolved_questions_present()
    assert TRACKING_ISSUE in release
    assert TRACKING_ISSUE in roadmap
    assert "## 0.42 — Production-grade Web Component platform" in roadmap
    assert "Stage 0 contract refined against Published `v0.41.0`" in roadmap
    assert "Living tip stays `v0.41.0` until cut" in roadmap


def test_phase042_medium_issues_are_cited() -> None:
    assert MEDIUM_ISSUES == (
        99,
        100,
        108,
        136,
        137,
        138,
        139,
        140,
        141,
        145,
        146,
        147,
        148,
        151,
        152,
        156,
        160,
        174,
        175,
        177,
        187,
        205,
        206,
        208,
        217,
        218,
        238,
        242,
        243,
        245,
        246,
        249,
    )
    assert len(MEDIUM_ISSUES) == 32
    assert not missing_refine_citations()


def test_phase042_no_cut_review_artifacts_yet() -> None:
    review_dir = ROOT / "docs" / "acceptance" / "security-review-042"
    assert (review_dir / "BRIEF.md").is_file()
    assert not (review_dir / "DISPOSITION.toml").is_file()
    assert not (review_dir / "REDACTED_REPORT.md").is_file()


def test_verified_gate_cannot_pass_without_executable_evidence(monkeypatch) -> None:
    import _gate_042

    monkeypatch.setattr(_gate_042, "gate_state", lambda _gate_id: "Verified")
    monkeypatch.setattr(_gate_042, "GATE_TESTS", {})
    assert _gate_042.check_gate("STABLE-042") == 1


def test_expected_gates_tuple_matches_manifest() -> None:
    assert set(EXPECTED_GATES) == EXPECTED_GATES_SET
    assert EXPECTED_GATES[-1] == "PKG-042"
