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
    """Best-effort semantic snapshot from rendered HTML (not a browser a11y tree)."""
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


def axe_to_sarif(
    violations: list[dict[str, Any]],
    *,
    tool_name: str = "axe-core",
    tool_version: str = "pinned",
) -> dict[str, Any]:
    """Stable SARIF-ish provenance for axe findings (TEST-019)."""
    results = []
    for item in violations:
        results.append(
            {
                "ruleId": item.get("id") or item.get("rule_id") or "unknown",
                "level": item.get("impact") or "warning",
                "message": {"text": item.get("description") or item.get("help") or str(item)},
                "locations": [
                    {"physicalLocation": {"artifactLocation": {"uri": n}}}
                    for n in (item.get("nodes") or [])[:5]
                    if isinstance(n, str)
                ],
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
