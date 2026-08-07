"""AccessibilityScenario, tree snapshots, and SARIF helpers (TEST-019)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Literal

__all__ = [
    "AccessibilityFinding",
    "AccessibilityScenario",
    "AccessibilityTreeNode",
    "axe_to_sarif",
    "snapshot_accessibility_tree",
]


@dataclass(frozen=True, slots=True)
class AccessibilityTreeNode:
    role: str
    name: str = ""
    tag: str = ""
    state: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AccessibilityFinding:
    rule_id: str
    impact: str
    message: str
    status: Literal["automatic", "semi-automatic", "manual"] = "automatic"
    nodes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "impact": self.impact,
            "message": self.message,
            "status": self.status,
            "nodes": list(self.nodes),
        }


@dataclass
class AccessibilityScenario:
    """Vocabulary for structured accessibility evidence steps."""

    name: str
    steps: list[str] = field(default_factory=list)
    covers: tuple[str, ...] = ()
    engine_versions: dict[str, str] = field(default_factory=dict)
    findings: list[AccessibilityFinding] = field(default_factory=list)

    def add_step(self, step: str) -> None:
        self.steps.append(step)

    def record_finding(self, finding: AccessibilityFinding) -> None:
        self.findings.append(finding)

    def summarize(self) -> dict[str, Any]:
        """Never claim 'accessible' from an empty scan."""
        if not self.findings:
            return {
                "name": self.name,
                "status": "incomplete",
                "summary": "No findings recorded — not evidence of accessibility",
                "accessible": False,
            }
        return {
            "name": self.name,
            "status": "recorded",
            "finding_count": len(self.findings),
            "accessible": False,
            "findings": [f.as_dict() for f in self.findings],
        }


_TAG_RE = re.compile(r"<([a-zA-Z0-9]+)([^>]*)>", re.M)
_ARIA_LABEL = re.compile(r'aria-label="([^"]*)"')
_ROLE = re.compile(r'role="([^"]*)"')
_ID = re.compile(r'\bid="([^"]*)"')


def snapshot_accessibility_tree(html: str) -> list[AccessibilityTreeNode]:
    """Markup heuristic from rendered HTML — **not** a browser accessibility tree.

    Prefer Playwright ``get_by_role`` for AT-019 live evidence. This helper is for
    offline structural smoke checks only.
    """
    nodes: list[AccessibilityTreeNode] = []
    for match in _TAG_RE.finditer(html):
        tag = match.group(1).lower()
        attrs = match.group(2)
        if tag in {"html", "head", "meta", "link", "script", "style", "br", "hr"}:
            continue
        role_m = _ROLE.search(attrs)
        label_m = _ARIA_LABEL.search(attrs)
        id_m = _ID.search(attrs)
        role = role_m.group(1) if role_m else _implicit_role(tag)
        name = label_m.group(1) if label_m else (id_m.group(1) if id_m else "")
        nodes.append(AccessibilityTreeNode(role=role, name=name, tag=tag))
    return nodes


def _implicit_role(tag: str) -> str:
    return {
        "button": "button",
        "a": "link",
        "nav": "navigation",
        "main": "main",
        "header": "banner",
        "footer": "contentinfo",
        "aside": "complementary",
        "form": "form",
        "img": "img",
        "h1": "heading",
        "h2": "heading",
        "h3": "heading",
        "h4": "heading",
        "h5": "heading",
        "h6": "heading",
        "input": "textbox",
        "select": "combobox",
        "textarea": "textbox",
        "table": "table",
    }.get(tag, tag)


def _node_location_uri(node: object) -> str | None:
    if isinstance(node, str):
        return node or None
    if not isinstance(node, dict):
        return None
    target = node.get("target")
    if isinstance(target, list) and target:
        return str(target[0])
    if isinstance(target, str) and target:
        return target
    html = node.get("html")
    if isinstance(html, str) and html:
        return html[:200]
    summary = node.get("failureSummary")
    if isinstance(summary, str) and summary:
        return summary[:200]
    return None


def axe_to_sarif(
    violations: list[dict[str, Any]],
    *,
    tool_name: str = "axe-core",
    tool_version: str = "pinned",
) -> dict[str, Any]:
    """Stable SARIF-ish provenance for axe findings (TEST-019)."""
    results = []
    for item in violations:
        locations = []
        for node in (item.get("nodes") or [])[:5]:
            uri = _node_location_uri(node)
            if uri:
                locations.append({"physicalLocation": {"artifactLocation": {"uri": uri}}})
        results.append(
            {
                "ruleId": item.get("id") or item.get("rule_id") or "unknown",
                "level": item.get("impact") or "warning",
                "message": {"text": item.get("description") or item.get("help") or str(item)},
                "locations": locations,
            }
        )
    return {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {"driver": {"name": tool_name, "version": tool_version}},
                "results": results,
                "properties": {
                    "hedron_gate": "TEST-019",
                    "empty_means_accessible": False,
                },
            }
        ],
    }
