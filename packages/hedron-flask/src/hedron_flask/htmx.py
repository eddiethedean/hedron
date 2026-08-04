"""HTMX request detection for Flask (portable core types only)."""

from __future__ import annotations

from collections.abc import Mapping

from hedron_core.htmx_contract import HtmxContext, htmx_context_from_headers
from hedron_core.rendering import RenderMode

__all__ = [
    "htmx_context",
    "is_htmx_request",
    "render_mode_for_request",
]


def is_htmx_request(headers: Mapping[str, str]) -> bool:
    return htmx_context_from_headers(dict(headers)).is_htmx


def htmx_context(headers: Mapping[str, str]) -> HtmxContext:
    return htmx_context_from_headers(dict(headers))


def render_mode_for_request(
    headers: Mapping[str, str],
    *,
    force: RenderMode | None = None,
) -> RenderMode:
    if force is not None:
        return force
    ctx = htmx_context(headers)
    if ctx.history_restore:
        return RenderMode.PAGE
    return RenderMode.FRAGMENT if ctx.is_htmx else RenderMode.PAGE
