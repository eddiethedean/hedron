"""Light-DOM extras host wrapper (LIFECYCLE-051). Aligns with RFC-0060 ABI."""

from __future__ import annotations

import json
from typing import Any

from hedron_core.component import NodeLike
from hedron_core.html import html


def extras_host(
    tag: str,
    *children: NodeLike,
    payload: dict[str, Any] | None = None,
    **kwargs: Any,
) -> NodeLike:
    """Wrap children in a registered extras custom element without a new ABI."""
    attrs: dict[str, Any] = dict(kwargs)
    data = dict(attrs.pop("data", {}) or {})
    raw = json.dumps(payload or {}, separators=(",", ":"), default=str)
    attrs["data-hedron-payload"] = raw
    if data:
        attrs["data"] = data
    return html.tag(tag)(*children, **attrs)
