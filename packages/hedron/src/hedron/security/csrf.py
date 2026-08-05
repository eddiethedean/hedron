"""CSRF token helpers for cookie-authenticated Hedron actions."""

from __future__ import annotations

import secrets
from typing import Any

from fastapi import HTTPException, Request, status
from starlette.responses import Response

from hedron.security.policy import SecurityPolicy, SecurityProfile

__all__ = [
    "csrf_token_for_request",
    "ensure_csrf_cookie",
    "extract_csrf_from_form",
    "generate_csrf_token",
    "prepare_csrf_from_request",
    "validate_csrf",
]


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def csrf_token_for_request(request: Request, policy: SecurityPolicy) -> str:
    """Return a single CSRF token for this request (cookie or request-scoped cache).

    Pages and ``ensure_csrf_cookie`` must share this value so form / ``hx-headers``
    tokens match the ``Set-Cookie`` value on first load.
    """
    existing = request.cookies.get(policy.csrf_cookie_name)
    if isinstance(existing, str) and existing:
        request.state.hedron_csrf_token = existing
        return existing
    cached = getattr(request.state, "hedron_csrf_token", None)
    if isinstance(cached, str) and cached:
        return cached
    value = generate_csrf_token()
    request.state.hedron_csrf_token = value
    return value


def ensure_csrf_cookie(
    response: Response,
    policy: SecurityPolicy,
    token: str | None = None,
    *,
    request: Request | None = None,
) -> str:
    """Set the CSRF cookie once, reusing the request-scoped token when present."""
    if request is not None and getattr(request.state, "hedron_csrf_cookie_set", False):
        cached = getattr(request.state, "hedron_csrf_token", None)
        if isinstance(cached, str) and cached:
            return cached
        existing = request.cookies.get(policy.csrf_cookie_name)
        if isinstance(existing, str) and existing:
            return existing
        # Flag was set without a real token — clear and take the normal Set-Cookie path.
        request.state.hedron_csrf_cookie_set = False

    if request is not None:
        value = token or csrf_token_for_request(request, policy)
    else:
        value = token or generate_csrf_token()

    secure = bool(request.url.is_secure) if request is not None else False
    if policy.profile is SecurityProfile.STRICT:
        # Strict always emits Secure cookies (including over plain HTTP TestClient).
        secure = True
    response.set_cookie(
        key=policy.csrf_cookie_name,
        value=value,
        httponly=False,
        samesite="lax",
        secure=secure,
        path="/",
    )
    if request is not None:
        request.state.hedron_csrf_cookie_set = True
        request.state.hedron_csrf_token = value
    return value


async def prepare_csrf_from_request(request: Request, policy: SecurityPolicy) -> None:
    """Populate form CSRF token from body when header is absent."""
    if not policy.csrf_enabled:
        return
    if request.headers.get(policy.csrf_header_name):
        return
    content_type = request.headers.get("content-type", "")
    if (
        "application/x-www-form-urlencoded" not in content_type
        and "multipart/form-data" not in content_type
    ):
        return
    try:
        form = await request.form()
    except Exception:  # noqa: BLE001 — malformed body falls through to validate
        return
    field_val = form.get(policy.csrf_form_field)
    if isinstance(field_val, str):
        request.state.hedron_csrf_form_token = field_val


def validate_csrf(request: Request, policy: SecurityPolicy) -> None:
    if not policy.csrf_enabled:
        return
    cookie = request.cookies.get(policy.csrf_cookie_name)
    header = request.headers.get(policy.csrf_header_name)
    form_token = getattr(request.state, "hedron_csrf_form_token", None)
    provided = header if isinstance(header, str) else None
    if provided is None and isinstance(form_token, str):
        provided = form_token
    if not cookie or not provided or not secrets.compare_digest(cookie, provided):
        from hedron_core.audit import SecurityAuditEventType, emit_security_audit

        emit_security_audit(
            SecurityAuditEventType.CSRF_REJECTED,
            "CSRF validation failed",
            attributes={"path": str(request.url.path), "method": request.method},
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF validation failed",
        )


def extract_csrf_from_form(
    data: Any,
    *,
    field_name: str = "csrf_token",
) -> str | None:
    if isinstance(data, dict):
        token = data.get(field_name)
        return token if isinstance(token, str) else None
    return None
