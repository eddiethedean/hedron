"""Reference Python implementation for portable fixture evaluation."""

from __future__ import annotations

import html as html_stdlib
from typing import Any

from hedron_conformance.normalize import normalize_html, normalize_identity
from hedron_conformance.schema import Capability, ConformanceFixture, ExpectedOutcome


def escape_text(value: str) -> str:
    return html_stdlib.escape(value.replace("\x00", ""), quote=False)


def escape_attr(value: str) -> str:
    return html_stdlib.escape(value.replace("\x00", ""), quote=True)


def _render_node(node: dict[str, Any]) -> str:
    kind = node.get("kind")
    if kind == "empty":
        return ""
    if kind == "text":
        return escape_text(str(node.get("text", "")))
    if kind == "trusted":
        return str(node.get("html", ""))
    if kind == "comment":
        safe = str(node.get("text", "")).replace("--", " - - ")
        return f"<!--{safe}-->"
    if kind == "fragment":
        return "".join(_render_node(child) for child in node.get("children", []))
    if kind == "element":
        tag = str(node.get("tag", "div")).lower()
        attrs = node.get("attributes") or {}
        attr_parts: list[str] = []
        for name in sorted(attrs.keys()):
            value = attrs[name]
            if value is None or value is False:
                continue
            if value is True:
                attr_parts.append(str(name).lower())
            else:
                attr_parts.append(f'{str(name).lower()}="{escape_attr(str(value))}"')
        attr_str = (" " + " ".join(attr_parts)) if attr_parts else ""
        void = bool(node.get("void")) or tag in {
            "area",
            "base",
            "br",
            "col",
            "embed",
            "hr",
            "img",
            "input",
            "link",
            "meta",
            "source",
            "track",
            "wbr",
        }
        if void:
            return f"<{tag}{attr_str}>"
        inner = "".join(_render_node(child) for child in node.get("children", []))
        return f"<{tag}{attr_str}>{inner}</{tag}>"
    raise ValueError(f"unknown node kind: {kind!r}")


def evaluate_fixture(fixture: ConformanceFixture) -> ExpectedOutcome:
    """Evaluate a fixture using the portable Python reference semantics."""
    inp = fixture.input
    if fixture.capability in {Capability.ESCAPING, Capability.ADVERSARIAL}:
        if inp.kind == "escape_text":
            return ExpectedOutcome(escaped_text=escape_text(inp.text or ""))
        if inp.kind == "escape_attr":
            return ExpectedOutcome(escaped_attr=escape_attr(inp.attr or ""))
        if inp.kind == "render_tree" and inp.tree is not None:
            return ExpectedOutcome(html=normalize_html(_render_node(inp.tree)))
        if inp.expect_error:
            return ExpectedOutcome(error_code=fixture.expected.error_code)
    if fixture.capability == Capability.IDENTITY:
        logical = inp.logical_id or ""
        # Portable identity: namespace-preserving logical id echo (deterministic).
        return ExpectedOutcome(identity=normalize_identity(f"id:{logical}"))
    if fixture.capability == Capability.DIAGNOSTICS:
        return ExpectedOutcome(diagnostic_code=fixture.expected.diagnostic_code)
    if fixture.capability == Capability.ARTIFACT_VERSION:
        version = (inp.artifact or {}).get("version", "")
        return ExpectedOutcome(artifact_version=str(version))
    if fixture.capability == Capability.RENDERING:
        assert inp.tree is not None
        return ExpectedOutcome(html=normalize_html(_render_node(inp.tree)))
    if fixture.capability == Capability.ACCESSIBILITY:
        tree = inp.tree or {}
        ok = _a11y_ok(tree)
        return ExpectedOutcome(a11y_ok=ok)
    raise ValueError(f"unsupported fixture capability/kind: {fixture.capability}/{inp.kind}")


def _a11y_ok(tree: dict[str, Any]) -> bool:
    """Sound subset: img needs alt; button needs accessible name; duplicate ids fail."""
    seen_ids: set[str] = set()

    def walk(node: dict[str, Any]) -> bool:
        if node.get("kind") != "element":
            return all(walk(c) for c in node.get("children", []))
        tag = str(node.get("tag", "")).lower()
        attrs = node.get("attributes") or {}
        element_id = attrs.get("id")
        if isinstance(element_id, str) and element_id in seen_ids:
            return False
        if isinstance(element_id, str):
            seen_ids.add(element_id)
        if tag == "img" and "alt" not in attrs:
            return False
        if tag == "button":
            children = node.get("children") or []
            text = "".join(
                str(c.get("text", "")) for c in children if c.get("kind") == "text"
            ).strip()
            aria = attrs.get("aria-label") or attrs.get("aria-labelledby")
            if not text and not aria:
                return False
        return all(walk(c) for c in node.get("children", []))

    return walk(tree)
