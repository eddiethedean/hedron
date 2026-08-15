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
    return hmac.compare_digest(expected, provided)


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
