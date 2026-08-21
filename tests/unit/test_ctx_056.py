"""CTX-056 evidence."""

from __future__ import annotations

import pytest

from hedron_core.security_plane import (
    SecurityContext,
    SecurityContextError,
    get_security_context,
    reset_security_context,
    set_security_context,
)


def test_ctx_056_immutable_narrow_and_serialize() -> None:
    ctx = SecurityContext(
        application_id="app-a",
        subject_id="user-1",
        tenant_id="tenant-1",
        scopes=frozenset({"read", "write"}),
        auth_level=2,
        correlation_id="corr-1",
    )
    narrowed = ctx.narrow(scopes=frozenset({"read"}), auth_level=1)
    assert narrowed.scopes == frozenset({"read"})
    with pytest.raises(SecurityContextError):
        ctx.narrow(scopes=frozenset({"admin"}))
    with pytest.raises(SecurityContextError):
        SecurityContext(application_id="app-a").narrow(subject_id="user-x")
    with pytest.raises(SecurityContextError):
        SecurityContext.from_serializable({**ctx.to_serializable(), "fingerprint": ""})
    with pytest.raises(SecurityContextError):
        SecurityContext.from_serializable({**ctx.to_serializable(), "scopes": "rw"})
    payload = ctx.to_serializable()
    restored = SecurityContext.from_serializable(payload, expected_application_id="app-a")
    assert restored.fingerprint == ctx.fingerprint
    with pytest.raises(SecurityContextError):
        SecurityContext.from_serializable(payload, expected_application_id="other")
    with pytest.raises(SecurityContextError):
        SecurityContext.from_serializable({**payload, "extra": "nope"})
    with pytest.raises(SecurityContextError):
        SecurityContext.from_serializable({**payload, "auth_level": 99})
    token = set_security_context(ctx)
    try:
        assert get_security_context() is ctx
    finally:
        reset_security_context(token)
    assert get_security_context() is None
