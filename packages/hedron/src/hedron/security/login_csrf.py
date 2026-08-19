"""Pre-authentication (login) CSRF helpers.

Distinct from post-login session CSRF in ``hedron.security.csrf``. Login forms
often run before a durable authenticated session exists; this module binds a
short-lived token to the anonymous session key / cookie name ``hedron_login_csrf``
(signed cookie optional via ``itsdangerous``). Use double-submit: embed the
issued token in the login form and validate it on POST. Adapter notes: Flask
and Django apps can store the same key on their session objects or set a
signed cookie with an application secret — Hedron does not own login routes.
"""

from __future__ import annotations

import secrets
from collections.abc import Mapping, MutableMapping
from typing import Any

from fastapi import HTTPException, status
from itsdangerous import BadSignature, BadTimeSignature, URLSafeTimedSerializer

from hedron_core.csrf import tokens_match

__all__ = [
    "LOGIN_CSRF_KEY",
    "issue_login_csrf",
    "sign_login_csrf",
    "unsign_login_csrf",
    "validate_login_csrf",
]

LOGIN_CSRF_KEY = "hedron_login_csrf"
_SALT = "hedron-login-csrf-v1"


def issue_login_csrf(
    session: MutableMapping[str, Any] | None = None,
    *,
    nbytes: int = 32,
) -> str:
    """Issue a login CSRF token and optionally store it under ``hedron_login_csrf``."""
    token = secrets.token_urlsafe(nbytes)
    if session is not None:
        session[LOGIN_CSRF_KEY] = token
    return token


def sign_login_csrf(token: str, secret: str, *, max_age: int | None = None) -> str:
    """Return a timed signed cookie value for ``hedron_login_csrf``."""
    del max_age  # signing itself is timeless; max_age applies at unsign
    serializer = URLSafeTimedSerializer(secret, salt=_SALT)
    return serializer.dumps(token)


def unsign_login_csrf(
    signed: str,
    secret: str,
    *,
    max_age: int = 600,
) -> str:
    """Decode a signed login CSRF cookie; raises ``ValueError`` when invalid/expired."""
    serializer = URLSafeTimedSerializer(secret, salt=_SALT)
    try:
        value = serializer.loads(signed, max_age=max_age)
    except (BadSignature, BadTimeSignature) as exc:
        raise ValueError("invalid or expired login CSRF cookie") from exc
    if not isinstance(value, str) or not value:
        raise ValueError("invalid login CSRF cookie payload")
    return value


def validate_login_csrf(
    token: str | None,
    *,
    session: Mapping[str, Any] | None = None,
    cookie: str | None = None,
    secret: str | None = None,
    max_age: int = 600,
) -> None:
    """Validate a submitted login CSRF token against session and/or signed cookie.

    Raises ``HTTPException`` 403 on failure.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Login CSRF validation failed",
        )

    expected_candidates: list[str] = []
    if session is not None:
        stored = session.get(LOGIN_CSRF_KEY)
        if isinstance(stored, str) and stored:
            expected_candidates.append(stored)

    if cookie and secret:
        try:
            expected_candidates.append(unsign_login_csrf(cookie, secret, max_age=max_age))
        except ValueError as exc:
            if not expected_candidates:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Login CSRF validation failed",
                ) from exc

    if not expected_candidates or not any(
        tokens_match(expected, token) for expected in expected_candidates
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Login CSRF validation failed",
        )
