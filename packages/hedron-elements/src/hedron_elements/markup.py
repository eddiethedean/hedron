"""Frozen element markup helpers (ABI-036)."""

from __future__ import annotations

import json
from collections.abc import Mapping
from html import escape
from typing import Any

from hedron_core.diagnostics import error

__all__ = [
    "MAX_STRUCTURED_BYTES",
    "MAX_STRUCTURED_DEPTH",
    "MAX_STRUCTURED_ITEMS",
    "encode_structured_input",
    "render_element_markup",
]

MAX_STRUCTURED_BYTES = 8192
MAX_STRUCTURED_ITEMS = 64
MAX_STRUCTURED_DEPTH = 4


def _depth(value: object, current: int = 0) -> int:
    if current > MAX_STRUCTURED_DEPTH:
        return current
    if isinstance(value, Mapping):
        return max((_depth(v, current + 1) for v in value.values()), default=current)
    if isinstance(value, (list, tuple)):
        return max((_depth(v, current + 1) for v in value), default=current)
    return current


def encode_structured_input(payload: Mapping[str, Any], *, instance_id: str) -> str:
    """Return an inert JSON script tag associated by instance id (never executed)."""
    try:
        raw = json.dumps(payload, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise error(
            "HED-ELEMENT-0005",
            title="Structured input encoding failed",
            explanation=str(exc),
            remediation="Provide JSON-serializable bounded configuration.",
        ) from exc
    if len(raw.encode("utf-8")) > MAX_STRUCTURED_BYTES:
        raise error(
            "HED-ELEMENT-0005",
            title="Structured input too large",
            explanation=f"Payload exceeds {MAX_STRUCTURED_BYTES} bytes.",
            remediation="Move large datasets to page/job endpoints.",
        )
    if isinstance(payload, Mapping) and len(payload) > MAX_STRUCTURED_ITEMS:
        raise error(
            "HED-ELEMENT-0005",
            title="Structured input item limit",
            explanation=f"Payload exceeds {MAX_STRUCTURED_ITEMS} items.",
            remediation="Reduce configuration size.",
        )
    if _depth(payload) > MAX_STRUCTURED_DEPTH:
        raise error(
            "HED-ELEMENT-0005",
            title="Structured input depth limit",
            explanation=f"Payload exceeds depth {MAX_STRUCTURED_DEPTH}.",
            remediation="Flatten configuration.",
        )
    safe_id = escape(instance_id, quote=True)
    # Escape closing tags inside JSON text nodes.
    safe_json = raw.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return f'<script type="application/json" data-hedron-input-for="{safe_id}">{safe_json}</script>'


def render_element_markup(
    *,
    tag_name: str,
    abi_version: int,
    element_id: str,
    attributes: Mapping[str, str] | None = None,
    server_content: str = "",
    instance_id: str | None = None,
    structured_input: Mapping[str, Any] | None = None,
) -> str:
    """Render frozen ABI markup for a light-DOM first-party element."""
    if not tag_name.startswith("hedron-") or "-" not in tag_name:
        raise error(
            "HED-ELEMENT-0003",
            title="Invalid element tag",
            explanation=f"Tag {tag_name!r} is not a valid first-party element name.",
            remediation="Use a hedron-* custom element tag.",
        )
    if abi_version < 1:
        raise error(
            "HED-ELEMENT-0002",
            title="Invalid ABI version",
            explanation=f"ABI {abi_version} is unsupported.",
            remediation="Use a positive ABI major.",
        )
    attrs = {
        "data-hedron-abi": str(abi_version),
        "data-hedron-element": element_id,
        **dict(attributes or {}),
    }
    if instance_id:
        attrs["data-hedron-input"] = instance_id
    attr_html = " ".join(f'{escape(k)}="{escape(str(v), quote=True)}"' for k, v in attrs.items())
    content = escape(server_content)
    body = (
        f'<{tag_name} {attr_html}><p data-hedron-server-region="content">{content}</p></{tag_name}>'
    )
    if structured_input is not None:
        if not instance_id:
            raise error(
                "HED-ELEMENT-0005",
                title="Structured input requires instance id",
                explanation="data-hedron-input association is required.",
                remediation="Pass instance_id with structured_input.",
            )
        body = encode_structured_input(structured_input, instance_id=instance_id) + body
    return body
