"""HTMX request detection and approved response headers (FastAPI adapter)."""

from __future__ import annotations

from starlette.requests import Request

from hedron_core.htmx.policy import InteractionPolicy
from hedron_core.htmx_contract import (
    APPROVED_REQUEST_HEADERS,
    APPROVED_RESPONSE_HEADERS,
    HtmxContext,
    approved_headers,
    htmx_context_from_headers,
    is_local_path,
    safe_css_selector,
)
from hedron_core.rendering import RenderMode

# Back-compat private alias used by builtins/reverse.
_safe_css_selector = safe_css_selector

__all__ = [
    "APPROVED_REQUEST_HEADERS",
    "APPROVED_RESPONSE_HEADERS",
    "HtmxContext",
    "approved_headers",
    "htmx_context",
    "is_htmx_request",
    "render_mode_for_request",
]


def is_htmx_request(request: Request) -> bool:
    return request.headers.get("HX-Request", "").lower() == "true"


def htmx_context(request: Request) -> HtmxContext:
    return htmx_context_from_headers(dict(request.headers))


def render_mode_for_request(
    request: Request,
    *,
    force: RenderMode | None = None,
    policy: InteractionPolicy | None = None,
) -> RenderMode:
    if force is not None:
        return force
    ctx = htmx_context(request)
    if policy is None:
        policy = getattr(getattr(request.app, "state", None), "hedron_interaction_policy", None)
    if ctx.boosted:
        return RenderMode.PAGE
    if ctx.history_restore:
        restore = getattr(policy, "history_restore", None) or "page"
        if restore == "page":
            return RenderMode.PAGE
        return RenderMode.FRAGMENT
    return RenderMode.FRAGMENT if ctx.is_htmx else RenderMode.PAGE


# Re-export for callers that imported _require_local_path indirectly via module attrs.
def _require_local_path(url: str, header_name: str) -> str:
    if not is_local_path(url):
        raise ValueError(f"{header_name} must be a local path")
    return url
