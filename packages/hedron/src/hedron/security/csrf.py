"""CSRF token helpers for cookie-authenticated Hedron actions."""

from __future__ import annotations

import secrets
from typing import Any

from fastapi import HTTPException, Request, status
from starlette.responses import Response

from hedron.security.policy import SecurityPolicy

__all__ = [
    "ensure_csrf_cookie",
    "generate_csrf_token",
    "validate_csrf",
]


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def ensure_csrf_cookie(response: Response, policy: SecurityPolicy, token: str | None = None) -> str:
    value = token or generate_csrf_token()
    response.set_cookie(
        key=policy.csrf_cookie_name,
        value=value,
        httponly=False,
        samesite="lax",
        secure=False,
        path="/",
    )
    return value


def validate_csrf(request: Request, policy: SecurityPolicy) -> None:
    if not policy.csrf_enabled:
        return
    cookie = request.cookies.get(policy.csrf_cookie_name)
    header = request.headers.get(policy.csrf_header_name)
    form_token: str | None = None
    # Prefer header; form field is checked by callers that already parsed the body.
    provided = header
    state_token = getattr(request.state, "hedron_csrf_form_token", None)
    if isinstance(state_token, str):
        form_token = state_token
    if provided is None:
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
