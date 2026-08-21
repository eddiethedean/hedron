"""EGRESS-056 evidence."""

from __future__ import annotations

import pytest

from hedron_core.security_plane import (
    EgressError,
    EgressPolicy,
    assert_ssrf_safe,
    decide_redirect_chain,
    policy_from_allowlist,
)


def test_egress_056_deny_by_default_and_redirects() -> None:
    deny = EgressPolicy(allowed_hosts=frozenset())
    with pytest.raises(EgressError):
        deny.require("https://evil.example/x")
    allow = policy_from_allowlist({"api.example"})
    decision = allow.require("https://api.example/v1")
    assert decision.reason == "allowed"
    with pytest.raises(EgressError):
        allow.require("https://api.example:8443/v1")
    chain = decide_redirect_chain(
        "https://api.example/a",
        ["https://api.example/b"],
        policy=allow,
    )
    assert len(chain) == 2
    with pytest.raises(EgressError):
        assert_ssrf_safe("http://127.0.0.1/admin")
