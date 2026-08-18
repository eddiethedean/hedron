"""Portable CSRF double-submit helpers (no framework types)."""

from __future__ import annotations

import hmac
import secrets

from hedron_core.security.secrets import redact_secret_like as redact_secret_like

__all__ = [
    "generate_csrf_token",
    "tokens_match",
    "validate_double_submit",
]


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def tokens_match(expected: str, provided: str) -> bool:
    if not expected or not provided:
        return False
    if not isinstance(expected, str) or not isinstance(provided, str):
        return False
    try:
        left = expected.encode("utf-8")
        right = provided.encode("utf-8")
    except (TypeError, UnicodeEncodeError):
        return False
    if len(left) != len(right):
        hmac.compare_digest(left, left)
        return False
    try:
        return hmac.compare_digest(left, right)
    except (TypeError, ValueError):
        return False


def validate_double_submit(
    *,
    cookie_token: str | None,
    form_token: str | None = None,
    header_token: str | None = None,
) -> bool:
    """Return True when cookie matches form or header token."""
    if not cookie_token:
        return False
    provided = form_token or header_token
    if not provided:
        return False
    return tokens_match(cookie_token, provided)
