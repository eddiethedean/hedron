"""Request-to-RenderContext adapter."""

from __future__ import annotations

from starlette.requests import Request

from hedron.security.csrf import csrf_token_for_request
from hedron_core.rendering import RenderContext
from hedron_core.security_policy import SecurityPolicy

__all__ = ["render_context_from_request"]


def render_context_from_request(request: Request) -> RenderContext:
    """Build a framework-neutral RenderContext without embedding the request."""
    locale = request.headers.get("Accept-Language", "en").split(",")[0].strip() or "en"
    theme = request.headers.get("X-Hedron-Theme")
    if not theme:
        theme = getattr(request.app.state, "hedron_theme", None)
    csrf_token: str | None = None
    csrf_form_field = "csrf_token"
    policy = getattr(request.app.state, "hedron_security", None)
    if isinstance(policy, SecurityPolicy) and policy.csrf_enabled:
        strategy = policy.resolve_csrf_strategy()
        if strategy is not None:
            csrf_form_field = strategy.form_field
            csrf_token = csrf_token_for_request(request, policy)
    return RenderContext.standalone(
        locale=locale,
        theme=theme if isinstance(theme, str) else None,
        csrf_token=csrf_token,
        csrf_form_field=csrf_form_field,
    )
