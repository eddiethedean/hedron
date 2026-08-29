"""AccessibilityScenario, tree snapshots, and SARIF helpers (TEST-019)."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Literal, cast

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
    state: dict[str, str] = field(default_factory=dict[str, str])


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
    steps: list[str] = field(default_factory=list[str])
    covers: tuple[str, ...] = ()
    engine_versions: dict[str, str] = field(default_factory=dict[str, str])
    findings: list[AccessibilityFinding] = field(default_factory=list[AccessibilityFinding])

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


_TAG_RE = re.compile(r"</?([a-zA-Z0-9]+)([^>]*)/?>", re.M)
_ARIA_LABEL = re.compile(r'aria-label="([^"]*)"')
_ROLE = re.compile(r'role="([^"]*)"')
_ID = re.compile(r'\bid="([^"]*)"')
_TYPE = re.compile(r'\btype="([^"]*)"', re.I)
_HREF = re.compile(r"\bhref=", re.I)
_VOID = frozenset(
    {"br", "hr", "img", "input", "meta", "link", "source", "track", "area", "col", "wbr"}
)
_SECTIONING = frozenset({"main", "article", "section", "aside", "nav"})

_INPUT_ROLES = {
    "text": "textbox",
    "search": "searchbox",
    "email": "textbox",
    "tel": "textbox",
    "url": "textbox",
    "password": "textbox",
    "number": "spinbutton",
    "checkbox": "checkbox",
    "radio": "radio",
    "submit": "button",
    "button": "button",
    "reset": "button",
    "image": "button",
    "range": "slider",
    "file": "button",
    "hidden": "none",
    "color": "textbox",
    "date": "textbox",
    "datetime-local": "textbox",
    "month": "textbox",
    "time": "textbox",
    "week": "textbox",
}


def snapshot_accessibility_tree(html: str) -> list[AccessibilityTreeNode]:
    """Markup heuristic from rendered HTML — **not** a browser accessibility tree.

    Prefer Playwright ``get_by_role`` for AT-019 live evidence. This helper is for
    offline structural smoke checks only.
    """
    nodes: list[AccessibilityTreeNode] = []
    sectioning_depth = 0
    for match in _TAG_RE.finditer(html):
        raw = match.group(0)
        tag = match.group(1).lower()
        attrs = match.group(2) or ""
        closing = raw.startswith("</")
        if closing:
            if tag in _SECTIONING and sectioning_depth > 0:
                sectioning_depth -= 1
            continue
        if tag in {"html", "head", "meta", "link", "script", "style", "br", "hr"}:
            continue
        role_m = _ROLE.search(attrs)
        label_m = _ARIA_LABEL.search(attrs)
        id_m = _ID.search(attrs)
        role = (
            role_m.group(1)
            if role_m
            else _implicit_role(tag, attrs, sectioning_depth=sectioning_depth)
        )
        if tag in _SECTIONING and tag not in _VOID and "/>" not in raw:
            sectioning_depth += 1
        if role == "none":
            continue
        name = label_m.group(1) if label_m else (id_m.group(1) if id_m else "")
        nodes.append(AccessibilityTreeNode(role=role, name=name, tag=tag))
    return nodes


def _implicit_role(tag: str, attrs: str = "", *, sectioning_depth: int = 0) -> str:
    if tag == "input":
        type_m = _TYPE.search(attrs)
        input_type = (type_m.group(1) if type_m else "text").lower()
        return _INPUT_ROLES.get(input_type, "textbox")
    if tag == "a":
        return "link" if _HREF.search(attrs) else "generic"
    if tag == "header":
        # Nested headers inside sectioning content are not document banners.
        return "generic" if sectioning_depth > 0 else "banner"
    if tag == "footer":
        return "generic" if sectioning_depth > 0 else "contentinfo"
    return {
        "button": "button",
        "nav": "navigation",
        "main": "main",
        "aside": "complementary",
        "form": "form",
        "img": "img",
        "h1": "heading",
        "h2": "heading",
        "h3": "heading",
        "h4": "heading",
        "h5": "heading",
        "h6": "heading",
        "select": "combobox",
        "textarea": "textbox",
        "table": "table",
    }.get(tag, tag)


def _node_location_uri(node: object) -> str | None:
    if isinstance(node, str):
        return node or None
    if not isinstance(node, dict):
        return None
    mapping = cast(dict[str, object], node)
    target = mapping.get("target")
    if isinstance(target, list) and target:
        return str(cast(list[object], target)[0])
    if isinstance(target, str) and target:
        return target
    html = mapping.get("html")
    if isinstance(html, str) and html:
        return html[:200]
    summary = mapping.get("failureSummary")
    if isinstance(summary, str) and summary:
        return summary[:200]
    return None


_SARIF_LEVELS = {
    "critical": "error",
    "serious": "error",
    "moderate": "warning",
    "minor": "note",
}


def axe_to_sarif(
    violations: Sequence[Mapping[str, object]],
    *,
    tool_name: str = "axe-core",
    tool_version: str = "pinned",
) -> dict[str, object]:
    """Stable SARIF 2.1.0 provenance for axe findings (TEST-019)."""
    results: list[dict[str, object]] = []
    rules: dict[str, dict[str, object]] = {}
    for item in violations:
        rule_id = str(item.get("id") or item.get("rule_id") or "unknown")
        impact = str(item.get("impact") or "moderate").lower()
        message = item.get("description") or item.get("help") or str(item)
        rules.setdefault(
            rule_id,
            {
                "id": rule_id,
                "name": rule_id,
                "shortDescription": {"text": str(message)},
                "fullDescription": {"text": str(item.get("help") or message)},
                "help": {"text": str(item.get("helpUrl") or item.get("help") or message)},
                "defaultConfiguration": {"level": _SARIF_LEVELS.get(impact, "warning")},
                "properties": {"axe_impact": impact},
            },
        )
        locations: list[dict[str, object]] = []
        raw_nodes = item.get("nodes")
        nodes = cast(Sequence[object], raw_nodes) if isinstance(raw_nodes, (list, tuple)) else ()
        for node in nodes[:5]:
            selector = _node_location_uri(node)
            if not selector:
                continue
            # CSS selectors are not file URIs — keep them as logical locations.
            locations.append(
                {
                    "logicalLocations": [{"fullyQualifiedName": selector, "kind": "css-selector"}],
                    "physicalLocation": {
                        "artifactLocation": {"uri": "about:blank"},
                        "region": {"snippet": {"text": selector}},
                    },
                }
            )
        results.append(
            {
                "ruleId": rule_id,
                "level": _SARIF_LEVELS.get(impact, "warning"),
                "message": {"text": str(message)},
                "locations": locations,
                "properties": {"axe_impact": impact},
            }
        )
    return {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": tool_name,
                        "version": tool_version,
                        "rules": list(rules.values()),
                    }
                },
                "results": results,
                "properties": {
                    "hedron_gate": "TEST-019",
                    "empty_means_accessible": False,
                },
            }
        ],
    }
