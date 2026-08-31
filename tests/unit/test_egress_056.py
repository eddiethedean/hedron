"""EGRESS-056 evidence."""

from __future__ import annotations

import pytest

from hedron_core.egress import bounded_response
from hedron_core.security_plane import (
    EgressError,
    EgressPolicy,
    assert_ssrf_safe,
    decide_redirect_chain,
    policy_from_allowlist,
)


def _public_resolver(_host: str) -> tuple[str, ...]:
    return ("8.8.8.8",)


def test_egress_056_deny_by_default_and_redirects() -> None:
    deny = EgressPolicy(allowed_hosts=frozenset())
    with pytest.raises(EgressError):
        deny.require("https://evil.example/x", resolver=_public_resolver)
    allow = policy_from_allowlist({"api.example"})
    decision = allow.require("https://api.example/v1", resolver=_public_resolver)
    assert decision.reason == "allowed"
    with pytest.raises(EgressError):
        allow.require("https://api.example:8443/v1", resolver=_public_resolver)
    with pytest.raises(EgressError):
        allow.require("https://api.example:0/v1", resolver=_public_resolver)
    chain = decide_redirect_chain(
        "https://api.example/a",
        ["https://api.example/b"],
        policy=allow,
        resolver=_public_resolver,
    )
    assert len(chain) == 2
    with pytest.raises(EgressError):
        assert_ssrf_safe("http://127.0.0.1/admin")
    with pytest.raises(EgressError):
        allow.require("https://api.example/v1", resolver=lambda _h: ())
    with pytest.raises(EgressError):
        allow.require("https://api.example/v1", resolver=lambda _h: ("100.64.1.1",))


def test_egress_rejects_malformed_urls_and_allows_public_hostnames(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    policy = EgressPolicy(allowed_hosts=frozenset({"api.example"}))
    monkeypatch.setattr("hedron_core.egress.default_resolve", _public_resolver)
    decision = policy.require("https://api.example/v1", resolver=_public_resolver)
    assert decision.reason == "allowed"
    for raw in ("https://api.example:abc/x", "https://api.example:99999/x", "https://[::1/x"):
        with pytest.raises(EgressError):
            policy.require(raw, resolver=_public_resolver)

    with pytest.raises(EgressError):
        assert_ssrf_safe("https://api.example:abc/x", policy=policy)


def test_egress_decision_carries_transport_budgets() -> None:
    policy = EgressPolicy(
        allowed_hosts=frozenset({"api.example"}),
        connect_deadline_seconds=2.5,
        response_budget_bytes=4,
    )
    decision = policy.require("https://api.example/v1", resolver=_public_resolver)
    assert decision.connect_deadline_seconds == 2.5
    assert decision.response_budget_bytes == 4
    assert bounded_response([b"ab", b"cd"], budget_bytes=4) == b"abcd"
    with pytest.raises(EgressError, match="budget"):
        bounded_response([b"abc", b"de"], budget_bytes=4)
