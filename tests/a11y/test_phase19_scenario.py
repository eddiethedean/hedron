"""Phase 0.19 TEST-019."""

from __future__ import annotations

from hedron_core import Button, Main, Nav, Text, render
from hedron_core.a11y import (
    AccessibilityFinding,
    AccessibilityScenario,
    axe_to_sarif,
    snapshot_accessibility_tree,
)


def test_scenario_empty_scan_not_accessible() -> None:
    scenario = AccessibilityScenario(name="demo", covers=("keyboard", "focus"))
    summary = scenario.summarize()
    assert summary["accessible"] is False
    assert summary["status"] == "incomplete"


def test_tree_snapshot_and_sarif_provenance() -> None:
    html = render(Main(Nav(Button("Go"), Text("x")))).html
    tree = snapshot_accessibility_tree(html)
    assert any(n.role in {"main", "navigation", "button"} for n in tree)
    scenario = AccessibilityScenario(name="axe")
    scenario.record_finding(
        AccessibilityFinding(rule_id="button-name", impact="critical", message="ok")
    )
    assert scenario.summarize()["finding_count"] == 1
    sarif = axe_to_sarif(
        [
            {
                "id": "label",
                "impact": "serious",
                "description": "missing",
                "nodes": [{"target": [".field"], "html": "<input>", "failureSummary": "Fix"}],
            }
        ]
    )
    assert sarif["runs"][0]["properties"]["empty_means_accessible"] is False
    assert sarif["runs"][0]["results"][0]["ruleId"] == "label"
    assert sarif["runs"][0]["results"][0]["level"] == "error"
    assert sarif["runs"][0]["results"][0]["properties"]["axe_impact"] == "serious"
    assert (
        sarif["runs"][0]["results"][0]["locations"][0]["physicalLocation"]["artifactLocation"][
            "uri"
        ]
        == ".field"
    )


def test_implicit_roles_for_input_types_and_anchors() -> None:
    html = (
        '<main><input type="checkbox" id="c1">'
        '<input type="radio" name="r">'
        '<input type="submit" value="Go">'
        '<a>No href</a><a href="/x">Link</a></main>'
    )
    tree = snapshot_accessibility_tree(html)
    roles = {(n.tag, n.role) for n in tree}
    assert ("input", "checkbox") in roles
    assert ("input", "radio") in roles
    assert ("input", "button") in roles
    assert ("a", "generic") in roles
    assert ("a", "link") in roles
