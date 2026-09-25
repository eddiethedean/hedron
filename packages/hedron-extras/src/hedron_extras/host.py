"""Light-DOM extras host wrapper (LIFECYCLE-051). Aligns with RFC-0060 ABI."""

from __future__ import annotations

import json

from hedron_core.component import NodeLike
from hedron_core.html import html

_BLOCKED_CLIENT_SCHEMES = ("javascript:", "data:", "vbscript:", "file:")


def reject_client_fetch_url(url: str | None, *, label: str) -> str | None:
    """Reject script-capable URLs used as browser fetch/event sources."""
    if url is None or url == "":
        return url
    lowered = url.strip().lower()
    if any(lowered.startswith(scheme) for scheme in _BLOCKED_CLIENT_SCHEMES):
        scheme = lowered.split(":", 1)[0]
        raise ValueError(f"{label} must not use a {scheme}: URL")
    return url


def extras_host(
    tag: str,
    *children: NodeLike,
    payload: dict[str, object] | None = None,
    **kwargs: object,
) -> NodeLike:
    """Wrap children in a registered extras custom element without a new ABI."""
    attrs: dict[str, object] = dict(kwargs)
    data = dict(attrs.pop("data", {}) or {})
    raw = json.dumps(payload or {}, separators=(",", ":"), default=str)
    attrs["data-hedron-payload"] = raw
    if data:
        attrs["data"] = data
    return html.tag(tag)(*children, **attrs)
