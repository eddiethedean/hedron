"""HTMX helper attrs for FastAPI built-ins."""

from __future__ import annotations

import json
from typing import Literal

from hedron.htmx import _safe_css_selector
from hedron.routing.reverse import ComponentRef
from hedron_core.component import NodeLike

__all__ = ["action_attrs", "oob_swap"]


def action_attrs(
    ref: ComponentRef,
    *,
    include_csrf: bool = False,
    csrf_token: str | None = None,
    csrf_header_name: str = "X-CSRF-Token",
) -> dict[str, str]:
    attrs = ref.hx_attrs()
    if include_csrf and csrf_token:
        attrs["hx-headers"] = json.dumps({csrf_header_name: csrf_token})
    return attrs


def oob_swap(
    element_id: str,
    content: NodeLike,
    *,
    swap: str = "innerHTML",
    tag: Literal["div", "section", "aside", "main", "nav"] = "div",
) -> NodeLike:
    """Mark a node for HTMX out-of-band swap via hx-swap-oob."""
    from hedron_core.interaction import oob_swap as core_oob_swap

    return core_oob_swap(element_id, content, swap=swap, tag=tag)


def safe_target(target: str | None) -> str | None:
    if target is None:
        return None
    if not _safe_css_selector(target):
        raise ValueError(f"Unsafe HTMX target selector: {target!r}")
    return target
