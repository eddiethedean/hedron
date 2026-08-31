"""Request-to-RenderContext adapter."""

from __future__ import annotations

from dataclasses import dataclass

from starlette.requests import Request

from hedron.security.csrf import csrf_token_for_request
from hedron_core.rendering import RenderContext
from hedron_core.security_policy import SecurityPolicy

__all__ = ["render_context_from_request"]


@dataclass(frozen=True, slots=True)
class _RequestRenderContext(RenderContext):
    """Private request transport details consumed by interactive components."""

    csrf_cookie_name: str = "hedron_csrf"
    csrf_header_name: str = "X-CSRF-Token"


def render_context_from_request(request: Request) -> RenderContext:
    """Build a framework-neutral RenderContext without embedding the request."""
    locale = request.headers.get("Accept-Language", "en").split(",")[0].strip() or "en"
    theme = request.headers.get("X-Hedron-Theme")
    if not theme:
        theme = getattr(request.app.state, "hedron_theme", None)
    csrf_token: str | None = None
    csrf_form_field = "csrf_token"
    csrf_cookie_name = "hedron_csrf"
    csrf_header_name = "X-CSRF-Token"
    policy = getattr(request.app.state, "hedron_security", None)
    if isinstance(policy, SecurityPolicy) and policy.csrf_enabled:
        strategy = policy.resolve_csrf_strategy()
        if strategy is not None:
            csrf_form_field = strategy.form_field
            csrf_cookie_name = strategy.cookie_name
            csrf_header_name = strategy.header_name
            csrf_token = csrf_token_for_request(request, policy)
    return _RequestRenderContext(
        locale=locale,
        theme=theme if isinstance(theme, str) else None,
        csrf_token=csrf_token,
        csrf_form_field=csrf_form_field,
        csrf_cookie_name=csrf_cookie_name,
        csrf_header_name=csrf_header_name,
        mount_path=_mount_path_from_request(request),
    )


def _mount_path_from_request(request: Request) -> str:
    from hedron.mount import mount_from_request

    state_mount = str(getattr(request.app.state, "hedron_mount_path", "") or "")
    configured = bool(getattr(request.app.state, "hedron_mount_was_configured", False))
    return state_mount if state_mount or configured else mount_from_request(request).path
