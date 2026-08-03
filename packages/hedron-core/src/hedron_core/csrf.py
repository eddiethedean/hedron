"""Portable CSRF double-submit helpers (no framework types)."""

from __future__ import annotations

import hmac
import secrets
from typing import Any

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


def redact_secret_like(value: Any, *, keys: frozenset[str] | None = None) -> Any:
    """Redact mapping values whose keys look secret-bearing."""
    secret_keys = keys or frozenset(
        {"password", "secret", "token", "api_key", "authorization", "cookie", "session"}
    )
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for k, v in value.items():  # type: ignore[assignment]
            key = str(k).lower()
            if any(s in key for s in secret_keys):
                out[str(k)] = "[redacted]"
            else:
                out[str(k)] = redact_secret_like(v, keys=secret_keys)
        return out
    if isinstance(value, list):
        return [redact_secret_like(v, keys=secret_keys) for v in value]  # type: ignore[misc]
    return value
