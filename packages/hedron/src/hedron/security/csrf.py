"""CSRF token helpers for cookie-authenticated Hedron actions."""

from __future__ import annotations

import os
from typing import Any

from fastapi import HTTPException, Request, status
from starlette.responses import Response

from hedron.security.policy import SecurityPolicy, SecurityProfile
from hedron_core.csrf import generate_csrf_token as _core_generate_csrf_token
from hedron_core.csrf_strategy import CsrfStrategy, CsrfValidationError

__all__ = [
    "csrf_token_for_request",
    "ensure_csrf_cookie",
    "extract_csrf_from_form",
    "generate_csrf_token",
    "prepare_csrf_from_request",
    "resolve_strategy",
    "validate_csrf",
]


def generate_csrf_token() -> str:
    return _core_generate_csrf_token()


def resolve_strategy(policy: SecurityPolicy) -> CsrfStrategy | None:
    return policy.resolve_csrf_strategy()


def _forwarded_proto_https(request: Request) -> bool:
    proto = request.headers.get("x-forwarded-proto", "")
    first = proto.split(",")[0].strip().lower() if proto else ""
    return first == "https"


def _trusted_proxy_peers(request: Request) -> set[str]:
    """Peers allowed to supply ``X-Forwarded-*`` (same allowlist model as mount)."""
    peers: set[str] = set()
    raw_env = os.environ.get("HEDRON_TRUSTED_PROXIES", "")
    peers.update(part.strip() for part in raw_env.split(",") if part.strip())
    scope = getattr(request, "scope", None)
    app = scope.get("app") if isinstance(scope, dict) else None
    state = getattr(app, "state", None) if app is not None else None
    configured = getattr(state, "hedron_trusted_peers", None) if state is not None else None
    if isinstance(configured, (list, tuple, set, frozenset)):
        peers.update(str(item).strip() for item in configured if str(item).strip())
    return peers


def _forwarded_proto_https_trusted(request: Request) -> bool:
    """Honor ``X-Forwarded-Proto: https`` only from allowlisted proxy peers."""
    if not _forwarded_proto_https(request):
        return False
    peers = _trusted_proxy_peers(request)
    if not peers:
        return False
    client = request.scope.get("client") if isinstance(request.scope, dict) else None
    peer = client[0] if isinstance(client, (list, tuple)) and client else None
    return peer is not None and peer in peers


def _csrf_cookie_should_be_secure(request: Request | None, policy: SecurityPolicy) -> bool:
    """Resolve Secure flag for CSRF cookies (Flask-parity + proxy awareness).

    STRICT always emits Secure cookies. ``HEDRON_ENV=production`` / ``prod`` also
    forces Secure (TLS is assumed at the edge). Otherwise DEVELOPMENT/STANDARD follow
    ``is_secure`` or trusted-peer ``X-Forwarded-Proto: https`` so TLS-terminating
    proxies still get Secure without letting arbitrary clients force the flag over
    plain HTTP.
    """
    if policy.profile is SecurityProfile.STRICT:
        return True
    from hedron_core.compile_gate import is_production_env

    if is_production_env():
        return True
    if request is None:
        return False
    return bool(request.url.is_secure) or _forwarded_proto_https_trusted(request)


def _strategy_names(strategy: CsrfStrategy) -> tuple[str, str, str | None]:
    form_field = strategy.form_field
    header_name = strategy.header_name
    cookie_name = getattr(strategy, "cookie_name", None)
    return form_field, header_name, cookie_name if isinstance(cookie_name, str) else None


def csrf_token_for_request(request: Request, policy: SecurityPolicy) -> str:
    """Return a single CSRF token for this request (cookie or request-scoped cache).

    Pages and ``ensure_csrf_cookie`` must share this value so form / ``hx-headers``
    tokens match the ``Set-Cookie`` value on first load.
    """
    strategy = resolve_strategy(policy)
    if strategy is None:
        return ""
    return strategy.issue(request)


def ensure_csrf_cookie(
    response: Response,
    policy: SecurityPolicy,
    token: str | None = None,
    *,
    request: Request | None = None,
) -> str:
    """Set the CSRF cookie once when the active strategy uses cookies."""
    strategy = resolve_strategy(policy)
    if strategy is None:
        return ""

    sets_cookie = bool(getattr(strategy, "sets_cookie", False))
    if not sets_cookie:
        if request is not None:
            return token or strategy.issue(request)
        return token or generate_csrf_token()

    cookie_name = getattr(strategy, "cookie_name", policy.csrf_cookie_name)
    if not isinstance(cookie_name, str) or not cookie_name:
        cookie_name = policy.csrf_cookie_name

    if request is not None and getattr(request.state, "hedron_csrf_cookie_set", False):
        cached = getattr(request.state, "hedron_csrf_token", None)
        if isinstance(cached, str) and cached:
            return cached
        existing = request.cookies.get(cookie_name)
        if isinstance(existing, str) and existing:
            return existing
        # Flag was set without a real token — clear and take the normal Set-Cookie path.
        request.state.hedron_csrf_cookie_set = False

    if request is not None:
        value = token or strategy.issue(request)
    else:
        value = token or generate_csrf_token()

    secure = _csrf_cookie_should_be_secure(request, policy)
    cookie_path = "/"
    if request is not None:
        # Prefer scope lookup: Request.app raises KeyError when ASGI scope lacks "app"
        # (common in unit tests that build Request(scope) without an application).
        scope = getattr(request, "scope", None)
        app = scope.get("app") if isinstance(scope, dict) else None
        state = getattr(app, "state", None) if app is not None else None
        configured = getattr(state, "hedron_cookie_path", None) if state is not None else None
        if isinstance(configured, str) and configured:
            cookie_path = configured
        else:
            from hedron.mount import mount_from_request

            cookie_path = mount_from_request(request).cookie_path
    response.set_cookie(
        key=cookie_name,
        value=value,
        httponly=False,
        samesite="lax",
        secure=secure,
        path=cookie_path,
    )
    if request is not None:
        request.state.hedron_csrf_cookie_set = True
        request.state.hedron_csrf_token = value
    return value


async def prepare_csrf_from_request(request: Request, policy: SecurityPolicy) -> None:
    """Populate form CSRF token from body when header is absent."""
    strategy = resolve_strategy(policy)
    if strategy is None:
        return
    form_field, header_name, _cookie = _strategy_names(strategy)
    if request.headers.get(header_name):
        return
    content_type = request.headers.get("content-type", "")
    if (
        "application/x-www-form-urlencoded" not in content_type
        and "multipart/form-data" not in content_type
    ):
        return
    try:
        form = await request.form()
    except Exception:
        return
    field_val = form.get(form_field)
    if isinstance(field_val, str):
        request.state.hedron_csrf_form_token = field_val


def validate_csrf(request: Request, policy: SecurityPolicy) -> None:
    strategy = resolve_strategy(policy)
    if strategy is None:
        return
    _form_field, header_name, _cookie = _strategy_names(strategy)
    header = request.headers.get(header_name)
    form_token = getattr(request.state, "hedron_csrf_form_token", None)
    header_value = header if isinstance(header, str) else None
    form_value = form_token if isinstance(form_token, str) else None
    try:
        strategy.validate(request, form_value=form_value, header_value=header_value)
    except CsrfValidationError:
        from hedron_core.audit import SecurityAuditEventType, emit_security_audit

        emit_security_audit(
            SecurityAuditEventType.CSRF_REJECTED,
            "CSRF validation failed",
            attributes={"path": str(request.url.path), "method": request.method},
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF validation failed",
        ) from None


def extract_csrf_from_form(
    data: Any,
    *,
    field_name: str = "csrf_token",
) -> str | None:
    if isinstance(data, dict):
        token = data.get(field_name)
        return token if isinstance(token, str) else None
    return None
