"""HTMX helper attrs for FastAPI built-ins."""

from __future__ import annotations

import json
from typing import Literal, cast

from hedron.htmx import safe_css_selector
from hedron.routing.reverse import ComponentRef
from hedron_core.component import NodeLike
from hedron_core.htmx.attrs import HtmxAttrs

__all__ = ["action_attrs", "oob_swap"]


def action_attrs(
    ref: object,
    *,
    include_csrf: bool = False,
    csrf_token: str | None = None,
    csrf_header_name: str = "X-CSRF-Token",
) -> dict[str, str]:
    if isinstance(ref, ComponentRef):
        attrs = {name: str(value) for name, value in ref.htmx_attributes().items()}
    else:
        # Compatibility for duck-typed route references used by older callers.
        legacy = getattr(ref, "hx_attrs", None)
        if not callable(legacy):
            raise TypeError("action_attrs requires a ComponentRef or hx_attrs-compatible object")
        attrs = cast(dict[str, str], legacy())
    if include_csrf and csrf_token:
        attrs.update(
            {
                name: str(value)
                for name, value in HtmxAttrs(headers=json.dumps({csrf_header_name: csrf_token}))
                .as_html_attrs()
                .items()
            }
        )
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
    if not safe_css_selector(target):
        raise ValueError(f"Unsafe HTMX target selector: {target!r}")
    return target
