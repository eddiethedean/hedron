"""Authenticated security-context transport contract."""

from __future__ import annotations

import pytest

from hedron_core.security_plane import SecurityContext, SecurityContextError


def _context() -> SecurityContext:
    return SecurityContext(
        application_id="app-a",
        subject_id="user-1",
        tenant_id="tenant-1",
        scopes=frozenset({"read", "write"}),
        auth_level=2,
    )


def test_authenticated_context_round_trip() -> None:
    payload = _context().to_authenticated("secret", audience="jobs", now=100)
    restored = SecurityContext.from_authenticated(
        payload,
        secret="secret",
        expected_application_id="app-a",
        expected_audience="jobs",
        now=120,
    )
    assert restored.application_id == "app-a"
    assert restored.scopes == frozenset({"read", "write"})


@pytest.mark.parametrize("field", ["context", "audience", "expires_at", "key_id"])
def test_authenticated_context_rejects_tampering(field: str) -> None:
    payload = _context().to_authenticated("secret", now=100)
    if field == "context":
        payload[field]["scopes"] = ["admin"]
    elif field == "audience":
        payload[field] = "other"
    elif field == "expires_at":
        payload[field] = 10_000
    else:
        payload[field] = "rotated"
    with pytest.raises(SecurityContextError):
        SecurityContext.from_authenticated(payload, secret="secret", now=120)


def test_authenticated_context_rejects_expiry_and_wrong_application() -> None:
    payload = _context().to_authenticated("secret", ttl_seconds=10, now=100)
    with pytest.raises(SecurityContextError):
        SecurityContext.from_authenticated(payload, secret="secret", now=200)
    with pytest.raises(SecurityContextError):
        SecurityContext.from_authenticated(
            payload,
            secret="secret",
            expected_application_id="other",
            now=105,
        )


def test_authenticated_context_rejects_oversized_scope_list() -> None:
    payload = _context().to_authenticated("secret", now=100)
    payload["context"]["scopes"] = [f"scope-{idx}" for idx in range(129)]
    with pytest.raises(SecurityContextError):
        SecurityContext.from_authenticated(payload, secret="secret", now=100)
