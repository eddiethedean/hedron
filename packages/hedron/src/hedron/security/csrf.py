"""CSRF token helpers for cookie-authenticated Hedron actions."""

from __future__ import annotations

import secrets
from typing import Any

from fastapi import HTTPException, Request, status
from starlette.responses import Response

from hedron.security.policy import SecurityPolicy, SecurityProfile

__all__ = [
    "ensure_csrf_cookie",
    "extract_csrf_from_form",
    "generate_csrf_token",
    "prepare_csrf_from_request",
    "validate_csrf",
]


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def ensure_csrf_cookie(
    response: Response,
    policy: SecurityPolicy,
    token: str | None = None,
    *,
    request: Request | None = None,
) -> str:
    """Set the CSRF cookie once, reusing an existing request cookie when present."""
    if request is not None and getattr(request.state, "hedron_csrf_cookie_set", False):
        existing = request.cookies.get(policy.csrf_cookie_name)
        cached = getattr(request.state, "hedron_csrf_token", None)
        if isinstance(cached, str):
            return cached
        return existing or token or generate_csrf_token()

    existing = request.cookies.get(policy.csrf_cookie_name) if request is not None else None
    value = token or existing or generate_csrf_token()
    secure = policy.profile is SecurityProfile.STRICT
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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF validation failed",
        )


def extract_csrf_from_form(data: Any) -> str | None:
    if isinstance(data, dict):
        token = data.get("csrf_token")
        return token if isinstance(token, str) else None
    return None
