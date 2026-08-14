from __future__ import annotations

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from _gate_038 import (  # noqa: E402
    CHART_SPEC,
    EXPECTED_GATES,
    FLEET_INVENTORY,
    GATE_TESTS,
    INVENTORY,
    MEDIUM_ISSUES,
    TRACKING_ISSUE,
    missing_refine_citations,
    rfc_resolved_questions_present,
)

EXPECTED_GATES_SET = {
    "GRAMMAR-038",
    "RENDER-038",
    "DESIGN-038",
    "VISUAL-038",
    "INTERACT-038",
    "A11Y-038",
    "PERF-038",
    "EXPORT-038",
    "SECURITY-038",
    "COMPAT-038",
    "DOCS-038",
    "REGRESS-038",
    "PKG-038",
}


def test_phase038_manifest_commands_exist() -> None:
    path = ROOT / "docs" / "acceptance" / "release-gate-0.38.toml"
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


def test_phase038_inventory_locks_web_component_and_budgets() -> None:
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    assert data["state"] in {"planned", "verified"}
    assert data["living_published_baseline"] == "v0.37.0"
    assert data["element"]["tag"] == "hedron-chart"
    assert data["element"]["paint"] == ["svg", "canvas"]
    assert "ChartSpec" in data["supported"]["authoring"]
    assert data["budgets"]["core_gzip_kib"] <= 90
    assert data["budgets"]["no_chart_route_bytes"] == 0
    assert data["compatibility"]["consumer_node_dependency"] is False
    assert data["bounds"]["max_rows"] == 10000
    assert data["bounds"]["canvas_mark_threshold"] in {2500, "2500", "stage1_lock"}
    assert data["bounds"]["workers"] == "absent_by_default"


def test_phase038_fleet_inventory_keeps_elements_incubator() -> None:
    data = tomllib.loads(FLEET_INVENTORY.read_text(encoding="utf-8"))
    assert data["baseline"] == "v0.37.0"
    assert data["state"] in {"planned", "verified"}
    assert "hedron_chart" in data["hedron-charts"]["supported"]
    assert "matplotlib_static" in data["hedron-charts"]["supported"]
    assert data["hedron-elements"]["disposition"] == "incubator"


def test_phase038_decision_and_rephased_roadmap_agree() -> None:
    decisions = (ROOT / "docs" / "DECISIONS.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs" / "ROADMAP.md").read_text(encoding="utf-8")
    rfc = (ROOT / "docs" / "rfcs" / "RFC-0069-HIGH-FIDELITY-CHARTS.md").read_text(encoding="utf-8")
    release = (ROOT / "docs" / "acceptance" / "RELEASE_0_38.md").read_text(encoding="utf-8")
    assert "| D-066 | Accepted |" in decisions
    assert "**Status:** Accepted" in rfc[:800]
    assert rfc_resolved_questions_present()
    assert TRACKING_ISSUE in release
    assert TRACKING_ISSUE in roadmap
    for heading in (
        "## 0.38 — High-fidelity declarative charts",
        "## 0.39 — Rich data and visualization elements",
        "## 0.40 — Web Component authoring and interoperability",
        "## 0.41 — Browser composition, state, and navigation",
        "## 0.42 — Production-grade Web Component platform",
    ):
        assert heading in roadmap


def test_phase038_medium_issues_are_cited() -> None:
    assert MEDIUM_ISSUES == (71, 72, 75, 81, 82, 83, 201, 239)
    assert not missing_refine_citations()


def test_phase038_chart_spec_catalogs_exist() -> None:
    text = CHART_SPEC.read_text(encoding="utf-8")
    assert "hedron-chart-spec/1" in text
    assert "HED-CHART-0020" in text
    assert "--hedron-chart-color-1" in text
    assert "inspect" in text


def test_verified_gate_cannot_pass_without_executable_evidence(monkeypatch) -> None:
    import _gate_038

    monkeypatch.setattr(_gate_038, "gate_state", lambda _gate_id: "Verified")
    monkeypatch.setattr(_gate_038, "GATE_TESTS", {})
    assert _gate_038.check_gate("GRAMMAR-038") == 1


def test_expected_gates_tuple_matches_manifest() -> None:
    assert set(EXPECTED_GATES) == EXPECTED_GATES_SET
    assert EXPECTED_GATES[-1] == "PKG-038"
