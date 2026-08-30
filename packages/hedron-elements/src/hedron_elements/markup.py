"""Frozen element markup helpers (ABI-036)."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from html import escape
from typing import Any, NoReturn, cast

from hedron_core._html_meta import FORBIDDEN_ATTRS, URL_ATTRS
from hedron_core.diagnostics import HedronError, error
from hedron_core.html import (  # pyright: ignore[reportPrivateUsage]  # security parity seam
    _is_safe_layout_style,  # pyright: ignore[reportPrivateUsage]
    _normalize_srcset,  # pyright: ignore[reportPrivateUsage]
)
from hedron_core.htmx_eval import (
    canonical_hx_attribute,
    hx_attribute_is_url,
    reject_hx_eval_value,
)
from hedron_core.security import SafeUrl, UrlPurpose

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

# Custom-element token: no quotes, spaces, ``>``, or ``/`` breakouts (#215).
_CUSTOM_ELEMENT_TAG = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)+$")
# Match hedron_core.html / _serializer attribute-name allowlist.
_SAFE_ATTR_NAME = re.compile(r"^[A-Za-z_][\w.-]*$")
_FROZEN_ATTR_NAMES = frozenset(
    {
        "data-hedron-abi",
        "data-hedron-element",
        "data-hedron-input",
    }
)


def _strip_nul(value: str) -> str:
    return value.replace("\x00", "")


def _require_element_tag(tag_name: str) -> str:
    tag = _strip_nul(tag_name).strip().lower()
    if not _CUSTOM_ELEMENT_TAG.match(tag) or not tag.startswith("hedron-"):
        raise error(
            "HED-ELEMENT-0003",
            title="Invalid element tag",
            explanation=f"Tag {tag_name!r} is not a valid first-party element name.",
            remediation="Use a hedron-* custom element tag matching [a-z][a-z0-9]*(-[a-z0-9]+)+.",
        )
    return tag


def _require_safe_attr_name(name: str) -> str:
    cleaned = _strip_nul(name)
    if not cleaned or not _SAFE_ATTR_NAME.match(cleaned) or any(ord(ch) < 32 for ch in cleaned):
        raise error(
            "HED-SEC-0010",
            title="Unsafe attribute name rejected",
            explanation=f"Attribute name {name!r} contains forbidden characters.",
            remediation="Use token attribute names matching [A-Za-z_][\\w.-]*.",
        )
    lower = cleaned.lower()
    if lower.startswith("on") or lower.startswith("hx-on"):
        raise error(
            "HED-SEC-0002",
            title="Inline event handler rejected",
            explanation=f"Attribute {name!r} is an inline event handler.",
            remediation="Use HTMX attributes or registered Web Components instead.",
        )
    return cleaned


def _url_purpose_for_attr(name: str) -> UrlPurpose:
    lower = name.lower()
    if lower in {"action", "formaction"}:
        return UrlPurpose.FORM_ACTION
    if lower in {"src", "poster", "ping"} or lower.endswith("src"):
        return UrlPurpose.ASSET
    return UrlPurpose.NAVIGATION


def _is_url_attribute(name: str) -> bool:
    lower = name.lower()
    return (
        lower in URL_ATTRS
        or lower.endswith("href")
        or lower.endswith("src")
        or hx_attribute_is_url(lower)
    )


def _raise_unsafe_url(canonical: str, cause: HedronError) -> NoReturn:
    raise error(
        "HED-SEC-0003",
        title="Unsafe URL rejected",
        explanation=f"Attribute {canonical!r} value is not a safe URL.",
        remediation=(
            "Pass a root-relative path; javascript/vbscript/data/file/blob are forbidden."
        ),
    ) from cause


def _normalize_element_attr_value(name: str, value: str) -> str:
    """Apply HTMX/url/style security parity with ``hedron_core.html`` (#237, #244)."""
    canonical = canonical_hx_attribute(name)
    lower = name.lower()
    reject_hx_eval_value(canonical, value)

    if lower in {"style", "style_"}:
        if _is_safe_layout_style(value):
            return str(value).strip().rstrip(";")
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
            remediation="Remove style/srcdoc and use typed theme or trusted assets later.",
        )

    if not _is_url_attribute(name):
        return value

    if lower == "srcset":
        try:
            return _normalize_srcset(value)
        except HedronError as exc:
            _raise_unsafe_url(canonical, exc)

    hx_url = canonical if hx_attribute_is_url(lower) else lower
    if hx_url in {"hx-push-url", "hx-replace-url"} and value.lower() in {"true", "false"}:
        return value.lower()

    purpose = _url_purpose_for_attr(hx_url if hx_url.startswith("hx-") else lower)
    try:
        parsed = SafeUrl.parse(value, purpose=purpose)
    except HedronError as exc:
        _raise_unsafe_url(canonical, exc)
    return parsed.value


def _depth(value: object, current: int = 0) -> int:
    if current > MAX_STRUCTURED_DEPTH:
        return current
    if isinstance(value, Mapping):
        values = cast(Mapping[object, object], value).values()
        return max((_depth(item, current + 1) for item in values), default=current)
    if isinstance(value, (list, tuple)):
        values = cast(list[object] | tuple[object, ...], value)
        return max((_depth(item, current + 1) for item in values), default=current)
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
    if len(payload) > MAX_STRUCTURED_ITEMS:
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
    safe_id = escape(_strip_nul(instance_id), quote=True)
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
    tag = _require_element_tag(tag_name)
    if abi_version < 1:
        raise error(
            "HED-ELEMENT-0002",
            title="Invalid ABI version",
            explanation=f"ABI {abi_version} is unsupported.",
            remediation="Use a positive ABI major.",
        )
    # Caller attributes first; frozen ABI identity always wins afterward (#215).
    attrs: dict[str, str] = {}
    for key, value in dict(attributes or {}).items():
        safe_key = _require_safe_attr_name(str(key))
        if safe_key.lower() in _FROZEN_ATTR_NAMES:
            raise error(
                "HED-ELEMENT-0003",
                title="Frozen element attribute rejected",
                explanation=f"Attribute {safe_key!r} is reserved for ABI identity markup.",
                remediation="Omit data-hedron-abi / data-hedron-element / data-hedron-input.",
            )
        attrs[safe_key] = _normalize_element_attr_value(safe_key, _strip_nul(str(value)))
    attrs["data-hedron-abi"] = str(abi_version)
    attrs["data-hedron-element"] = _strip_nul(element_id)
    if instance_id:
        attrs["data-hedron-input"] = _strip_nul(instance_id)
    attr_html = " ".join(
        f'{escape(k, quote=True)}="{escape(str(v), quote=True)}"' for k, v in attrs.items()
    )
    content = escape(_strip_nul(server_content))
    body = f'<{tag} {attr_html}><p data-hedron-server-region="content">{content}</p></{tag}>'
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
