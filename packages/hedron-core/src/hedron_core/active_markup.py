"""Shared active-content rejection for trusted SVG / icon markup."""

from __future__ import annotations

import html as html_stdlib
import re

from hedron_core.security import contains_dangerous_scheme

__all__ = [
    "active_markup_reason",
    "has_active_markup",
]


_BANNED_TAGS = (
    "<script",
    "<foreignobject",
    "<iframe",
    "<object",
    "<embed",
)

# Quoted or unquoted remote / protocol-relative hrefs.
_REMOTE_HREF = re.compile(
    r"(?:^|[\s\"'/])(?:xlink:)?href\s*=\s*(?:[\"']\s*)?(?:https?:)?//",
    re.IGNORECASE,
)
# SMIL can assign event-handler attribute names at runtime.
_SMIL_ON_ATTR = re.compile(
    r"<(?:set|animate|animateTransform)\b[^>]*\battributeName\s*=\s*[\"']?\s*on[a-z]+",
    re.IGNORECASE,
)


def _scan_payload(payload: str) -> str | None:
    lowered = payload.lower()
    if any(token in lowered for token in _BANNED_TAGS):
        return "banned active tag"
    if contains_dangerous_scheme(payload):
        return "dangerous URL scheme"
    if re.search(r"(?:^|[\s\"'/])on[a-z]+\s*=", lowered):
        return "event handler attribute"
    if _SMIL_ON_ATTR.search(payload) is not None:
        return "SMIL event handler attribute"
    if _REMOTE_HREF.search(payload) is not None:
        return "remote href"
    return None


def _entity_protected_decode(svg: str) -> str:
    """Decode entities while keeping escaped tag delimiters inert for scanning."""
    protected = (
        svg.replace("&lt;", "\0LT\0")
        .replace("&gt;", "\0GT\0")
        .replace("&#60;", "\0LT\0")
        .replace("&#62;", "\0GT\0")
        .replace("&#x3c;", "\0LT\0")
        .replace("&#x3e;", "\0GT\0")
        .replace("&#x3C;", "\0LT\0")
        .replace("&#x3E;", "\0GT\0")
    )
    scanned = protected
    for _ in range(3):
        decoded = html_stdlib.unescape(scanned)
        if decoded == scanned:
            break
        scanned = decoded
    return scanned


def active_markup_reason(svg: str) -> str | None:
    """Return a short reason when markup contains active content, else None."""
    reason = _scan_payload(svg)
    if reason is not None:
        return reason
    return _scan_payload(_entity_protected_decode(svg))


def has_active_markup(svg: str) -> bool:
    return active_markup_reason(svg) is not None
