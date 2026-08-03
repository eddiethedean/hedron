"""Request-to-RenderContext adapter."""

from __future__ import annotations

from starlette.requests import Request

from hedron_core.rendering import RenderContext

__all__ = ["render_context_from_request"]


def render_context_from_request(request: Request) -> RenderContext:
    """Build a framework-neutral RenderContext without embedding the request."""
    locale = request.headers.get("Accept-Language", "en").split(",")[0].strip() or "en"
    theme = request.headers.get("X-Hedron-Theme")
    return RenderContext.standalone(locale=locale, theme=theme)
