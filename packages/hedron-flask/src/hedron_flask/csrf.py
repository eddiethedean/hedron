"""CSRF double-submit cookie helpers for Flask (same token semantics as FastAPI adapter)."""

from __future__ import annotations

import secrets
from typing import TYPE_CHECKING

from werkzeug.exceptions import Forbidden

if TYPE_CHECKING:
    from flask import Request, Response

__all__ = [
    "csrf_token_for_request",
    "ensure_csrf_cookie",
    "extract_csrf_from_form",
    "generate_csrf_token",
    "validate_csrf",
]

DEFAULT_CSRF_COOKIE = "hedron_csrf"
DEFAULT_CSRF_HEADER = "X-CSRF-Token"


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def csrf_token_for_request(
    request: Request,
    *,
    cookie_name: str = DEFAULT_CSRF_COOKIE,
) -> str:
    existing = request.cookies.get(cookie_name)
    if isinstance(existing, str) and existing:
        return existing
    cached = getattr(request, "_hedron_csrf_token", None)
    if isinstance(cached, str) and cached:
        return cached
    value = generate_csrf_token()
    request._hedron_csrf_token = value  # type: ignore[attr-defined]
    return value


def ensure_csrf_cookie(
    response: Response,
    token: str,
    *,
    cookie_name: str = DEFAULT_CSRF_COOKIE,
    secure: bool = False,
) -> None:
    response.set_cookie(
        cookie_name,
        token,
        httponly=False,
        samesite="Lax",
        secure=secure,
        path="/",
    )


def extract_csrf_from_form(form: dict[str, str], *, field_name: str = "csrf_token") -> str | None:
    value = form.get(field_name)
    return value if isinstance(value, str) and value else None


def validate_csrf(
    request: Request,
    *,
    cookie_name: str = DEFAULT_CSRF_COOKIE,
    header_name: str = DEFAULT_CSRF_HEADER,
    form_field: str = "csrf_token",
) -> None:
    cookie = request.cookies.get(cookie_name)
    if not cookie:
        from hedron_core.audit import SecurityAuditEventType, emit_security_audit

        emit_security_audit(
            SecurityAuditEventType.CSRF_REJECTED,
            "Missing CSRF cookie",
            attributes={"path": request.path, "method": request.method},
        )
        raise Forbidden("Missing CSRF cookie")
    submitted = request.headers.get(header_name)
    if not submitted and request.form:
        submitted = extract_csrf_from_form(dict(request.form), field_name=form_field)
    if not submitted or not secrets.compare_digest(cookie, submitted):
        from hedron_core.audit import SecurityAuditEventType, emit_security_audit

        emit_security_audit(
            SecurityAuditEventType.CSRF_REJECTED,
            "Invalid CSRF token",
            attributes={"path": request.path, "method": request.method},
        )
        raise Forbidden("Invalid CSRF token")
