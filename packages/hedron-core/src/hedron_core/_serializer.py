"""Private deterministic HTML serializer."""

from __future__ import annotations

import html as html_stdlib
import logging
from collections.abc import Mapping

from hedron_core._html.policy import default_html_policy
from hedron_core._html_meta import (
    ATTR_ORDER,
    BOOLEAN_ATTRS,
    FORBIDDEN_ATTRS,
    FORBIDDEN_TAGS,
    URL_ATTRS,
    VOID_TAGS,
)
from hedron_core._nodes import (
    CommentNode,
    ComponentBoundaryNode,
    ElementNode,
    EmptyNode,
    FragmentNode,
    Node,
    TextNode,
    TrustedHtmlNode,
)
from hedron_core.diagnostics import error
from hedron_core.htmx_eval import hx_attribute_is_url, reject_hx_eval_value
from hedron_core.mount import prefix_local_path
from hedron_core.security import SafeUrl, check_url_purpose_for_attribute
from hedron_core.typing_aliases import HtmlAttrValue

_logger = logging.getLogger("hedron.core.serializer")


def _load_escape() -> tuple[object, object]:
    """Load optional hedron-native escape helpers (they honor HEDRON_NATIVE_DISABLE)."""
    try:
        from hedron_native import escape_attr as native_attr
        from hedron_native import escape_text as native_text

        return native_text, native_attr
    except ImportError as exc:
        # Missing optional accel is Supported — fall back to stdlib html.escape.
        _logger.debug("hedron_native unavailable; using stdlib escape: %s", exc)
        return None, None


_native_escape_text, _native_escape_attr = _load_escape()


def escape_text(value: str) -> str:
    # Strip NUL so it cannot survive into HTML text nodes.
    if _native_escape_text is not None:
        return _native_escape_text(value)  # type: ignore[operator]
    return html_stdlib.escape(value.replace("\x00", ""), quote=False)


def escape_attr(value: str) -> str:
    if _native_escape_attr is not None:
        return _native_escape_attr(value)  # type: ignore[operator]
    return html_stdlib.escape(value.replace("\x00", ""), quote=True)


def _require_safe_attr_name(name: str) -> None:
    default_html_policy.require_safe_attr_name(name)


def _attr_sort_key(name: str) -> tuple[int, str]:
    try:
        return (ATTR_ORDER.index(name), name)
    except ValueError:
        return (len(ATTR_ORDER), name)


def _format_attr(name: str, value: HtmlAttrValue, *, mount_path: str = "") -> str | None:
    if value is None:
        return None
    _require_safe_attr_name(name)
    lower = name.lower()
    if lower.startswith("on"):
        raise error(
            "HED-SEC-0002",
            title="Inline event handler rejected",
            explanation=f"Attribute {name!r} is an inline event handler.",
            remediation="Use HTMX attributes or registered Web Components instead.",
        )
    reject_hx_eval_value(lower, value)
    if lower == "style":
        if default_html_policy.is_safe_layout_style(value):
            from html import escape

            return f'style="{escape(str(value).strip().rstrip(";"), quote=True)}"'
        raise error(
            "HED-SEC-0007",
            title="Forbidden attribute",
            explanation=f"Attribute {name!r} is not permitted under baseline policy.",
            remediation="Only layout custom properties like '--hedron-gap: 1rem' are allowed.",
        )
    if lower in FORBIDDEN_ATTRS:
        raise error(
            "HED-SEC-0007",
            title="Forbidden attribute",
            explanation=f"Attribute {name!r} is not permitted under baseline policy.",
            remediation="Remove style/srcdoc attributes.",
        )
    if lower in BOOLEAN_ATTRS:
        if value is False:
            return None
        if value is True or value == lower or value == "":
            return lower
        raise error(
            "HED-HTML-0001",
            title="Invalid boolean attribute value",
            explanation=f"Boolean attribute {name!r} received {value!r}.",
            remediation="Pass True, False, or None.",
        )
    if lower in {"hx-push-url", "hx-replace-url"}:
        # HTMX accepts boolean true/false in addition to a URL for history control.
        if isinstance(value, bool):
            return f'{lower}="{"true" if value else "false"}"'
        if isinstance(value, str) and value.lower() in {"true", "false"}:
            return f'{lower}="{value.lower()}"'
        if isinstance(value, SafeUrl):
            check_url_purpose_for_attribute(value, lower)
            return f'{lower}="{escape_attr(prefix_local_path(value.value, mount_path))}"'
        raise error(
            "HED-SEC-0003",
            title="URL attribute requires SafeUrl",
            explanation=(
                f"Attribute {name!r} must be a SafeUrl, bool, or 'true'/'false', "
                f"not {type(value)!r}."
            ),
            remediation="Pass True/False or SafeUrl.parse(...).",
        )

    if (
        lower in URL_ATTRS
        or hx_attribute_is_url(lower)
        or lower.endswith("href")
        or lower.endswith("src")
    ):
        if lower == "srcset" and isinstance(value, str):
            # Construction already validates candidates; re-check schemes at serialize.
            text = default_html_policy.normalize_srcset(value)
            candidates: list[str] = []
            for candidate in text.split(","):
                tokens = candidate.strip().split()
                if tokens:
                    tokens[0] = prefix_local_path(tokens[0], mount_path)
                    candidates.append(" ".join(tokens))
            text = ", ".join(candidates)
        elif isinstance(value, SafeUrl):
            check_url_purpose_for_attribute(value, lower)
            text = prefix_local_path(value.value, mount_path)
        elif isinstance(value, str):
            raise error(
                "HED-SEC-0003",
                title="URL attribute requires SafeUrl",
                explanation=(f"Attribute {name!r} must be a SafeUrl, not a raw string."),
                remediation="Wrap the URL with SafeUrl.parse(...).",
            )
        else:
            raise error(
                "HED-SEC-0003",
                title="URL attribute requires SafeUrl",
                explanation=f"Attribute {name!r} has unsupported type {type(value)!r}.",
                remediation="Pass a SafeUrl instance.",
            )
        return f'{lower}="{escape_attr(text)}"'

    if isinstance(value, SafeUrl):
        text = value.value
    elif isinstance(value, bool):
        text = "true" if value else "false"
    elif isinstance(value, (int, float)):
        text = str(value)
    elif isinstance(value, str):
        text = value
    else:
        raise error(
            "HED-HTML-0002",
            title="Unsupported attribute value",
            explanation=f"Attribute {name!r} has unsupported type {type(value)!r}.",
            remediation="Use str, bool, number, or SafeUrl values.",
        )
    return f'{lower}="{escape_attr(text)}"'


def serialize_attributes(attributes: Mapping[str, HtmlAttrValue], *, mount_path: str = "") -> str:
    parts: list[str] = []
    for name in sorted(attributes.keys(), key=_attr_sort_key):
        formatted = _format_attr(name, attributes[name], mount_path=mount_path)
        if formatted is not None:
            parts.append(formatted)
    if not parts:
        return ""
    return " " + " ".join(parts)


def serialize_node(node: Node, *, mount_path: str = "") -> str:
    if isinstance(node, EmptyNode):
        return ""
    if isinstance(node, TextNode):
        return escape_text(node.text)
    if isinstance(node, TrustedHtmlNode):
        return node.html
    if isinstance(node, CommentNode):
        safe = node.text.replace("--", " - - ")
        return f"<!--{safe}-->"
    if isinstance(node, FragmentNode):
        return "".join(serialize_node(child, mount_path=mount_path) for child in node.children)
    if isinstance(node, ComponentBoundaryNode):
        return "".join(serialize_node(child, mount_path=mount_path) for child in node.children)
    if isinstance(node, ElementNode):
        tag = node.tag.lower()
        if tag in FORBIDDEN_TAGS:
            raise error(
                "HED-SEC-0009",
                title="Active HTML element rejected",
                explanation=f"<{tag}> cannot be serialized under baseline policy.",
            )
        attrs = serialize_attributes(node.attributes, mount_path=mount_path)
        if node.void or tag in VOID_TAGS:
            if node.children:
                raise error(
                    "HED-HTML-0003",
                    title="Void element cannot have children",
                    explanation=f"<{tag}> is a void element and cannot contain children.",
                    remediation="Remove children from void elements.",
                )
            return f"<{tag}{attrs}>"
        inner = "".join(serialize_node(child, mount_path=mount_path) for child in node.children)
        return f"<{tag}{attrs}>{inner}</{tag}>"
    raise error(
        "HED-RENDER-0001",
        title="Unknown node type",
        explanation=f"Cannot serialize {type(node)!r}.",
    )


def serialize_tree(nodes: tuple[Node, ...] | Node, *, mount_path: str = "") -> str:
    if isinstance(nodes, tuple):
        return "".join(serialize_node(n, mount_path=mount_path) for n in nodes)
    return serialize_node(nodes, mount_path=mount_path)
