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


# Remote CSS @import (including protocol-relative and quoted forms).
_CSS_IMPORT = re.compile(
    r"@import\b[^;]*?(?:url\s*\(\s*)?[\"']?\s*(?:https?:)?//",
    re.IGNORECASE,
)
# SMIL set/animate/animateTransform elements (#239 / #261).
_SMIL_ELEMENT = re.compile(
    r"<(?:set|animate|animateTransform)\b(?P<attrs>[^>]*)>",
    re.IGNORECASE,
)
_SMIL_ATTR = re.compile(
    r"""\b(?P<name>[\w:.-]+)\s*=\s*(?:"(?P<dquot>[^"]*)"|'(?P<squot>[^']*)'|(?P<bare>[^\s>]+))""",
    re.IGNORECASE,
)
_REMOTE_URL_START = re.compile(r"(?:https?:)?//", re.IGNORECASE)


def _attr_value(match: re.Match[str]) -> str:
    return match.group("dquot") or match.group("squot") or match.group("bare") or ""


def _smil_remote_href_mutation(payload: str) -> bool:
    """True when SMIL assigns a remote URL to href / xlink:href via to= or values=.

    Attribute order is irrelevant. ``values`` keyframes are split on ``;``.
    """
    for element in _SMIL_ELEMENT.finditer(payload):
        attrs = {
            m.group("name").lower(): _attr_value(m)
            for m in _SMIL_ATTR.finditer(element.group("attrs"))
        }
        attr_name = attrs.get("attributename", "").strip().lower()
        if attr_name not in {"href", "xlink:href"}:
            continue
        assignments: list[str] = []
        if "to" in attrs:
            assignments.append(attrs["to"])
        if "values" in attrs:
            assignments.extend(attrs["values"].split(";"))
        if any(_REMOTE_URL_START.match(part.strip()) is not None for part in assignments):
            return True
    return False


def _scan_payload(payload: str) -> str | None:
    # #81: NUL bytes can split scanners; strip before matching.
    if "\x00" in payload:
        payload = payload.replace("\x00", "")
    lowered = payload.lower()
    if any(token in lowered for token in _BANNED_TAGS):
        return "banned active tag"
    if contains_dangerous_scheme(payload):
        return "dangerous URL scheme"
    if re.search(r"(?:^|[\s\"'/])on[a-z]+\s*=", lowered):
        return "event handler attribute"
    if _SMIL_ON_ATTR.search(payload) is not None:
        return "SMIL event handler attribute"
    if _smil_remote_href_mutation(payload):
        return "SMIL remote href mutation"
    if _REMOTE_HREF.search(payload) is not None:
        return "remote href"
    # #201: remote CSS @import
    if _CSS_IMPORT.search(payload) is not None or "@import" in lowered and "//" in lowered:
        return "remote css import"
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
