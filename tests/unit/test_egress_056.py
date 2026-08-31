"""EGRESS-056 connection-bound policy evidence."""

from __future__ import annotations

import gzip
from collections.abc import Callable, Iterable, Mapping

import pytest

from hedron_core.egress import (
    EgressDecision,
    EgressResponse,
    EgressTransportError,
    bounded_response,
    fetch_with_policy,
)
from hedron_core.request_budget import (
    RequestBudget,
    RequestBudgetLimits,
    reset_request_budget,
    set_request_budget,
)
from hedron_core.security_plane import (
    EgressError,
    EgressPolicy,
    assert_ssrf_safe,
    decide_redirect_chain,
    policy_from_allowlist,
)


def _public_resolver(_host: str) -> tuple[str, ...]:
    return ("8.8.8.8",)


class _ScriptedTransport:
    def __init__(self, *items: EgressResponse | Exception) -> None:
        self.items = list(items)
        self.decisions: list[EgressDecision] = []

    def request(self, *, decision: EgressDecision) -> EgressResponse:
        self.decisions.append(decision)
        item = self.items.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def _response(
    body: bytes | Iterable[bytes] = b"ok",
    *,
    status: int = 200,
    headers: Mapping[str, str] | None = None,
    peer: str = "8.8.8.8",
    via_proxy: bool = False,
    close: Callable[[], None] = lambda: None,
) -> EgressResponse:
    return EgressResponse(
        status_code=status,
        headers=headers or {},
        body=body,
        connected_address=peer,
        via_proxy=via_proxy,
        close=close,
    )


def test_egress_056_deny_by_default_exact_allowlists_and_redirects() -> None:
    deny = EgressPolicy(allowed_hosts=frozenset())
    with pytest.raises(EgressError, match="host_denied"):
        deny.require("https://evil.example/x", resolver=_public_resolver)
    allow = policy_from_allowlist(
        {"api.example"}, allowed_origins=frozenset({"https://api.example"})
    )
    decision = allow.require("https://api.example/v1", resolver=_public_resolver)
    assert decision.reason == "allowed"
    assert decision.origin == "https://api.example"
    with pytest.raises(EgressError, match="port_denied"):
        allow.require("https://api.example:8443/v1", resolver=_public_resolver)
    with pytest.raises(EgressError, match="origin_denied"):
        allow.require("https://api.example:80/v1", resolver=_public_resolver)
    chain = decide_redirect_chain(
        "https://api.example/a",
        ["/b"],
        policy=allow,
        resolver=_public_resolver,
    )
    assert [item.url for item in chain] == [
        "https://api.example/a",
        "https://api.example/b",
    ]


@pytest.mark.parametrize(
    "address",
    [
        "127.0.0.1",
        "::ffff:127.0.0.1",
        "100.64.1.1",
        "169.254.169.254",
        "0.0.0.0",
    ],
)
def test_egress_rejects_every_non_global_resolved_address(address: str) -> None:
    policy = EgressPolicy(allowed_hosts=frozenset({"api.example"}))
    with pytest.raises(EgressError, match="private_address_denied"):
        policy.require("https://api.example/x", resolver=lambda _host: ("8.8.8.8", address))


@pytest.mark.parametrize(
    "raw",
    [
        "http://127.1/admin",
        "http://0177.0.0.1/admin",
        "http://[::ffff:127.0.0.1]/admin",
        "https://user:secret@api.example/x",
        "https://api.example:abc/x",
        "https://api.example:99999/x",
        "https://[::1/x",
    ],
)
def test_egress_rejects_alternate_ip_userinfo_and_malformed_urls(raw: str) -> None:
    policy = EgressPolicy(
        allowed_schemes=frozenset({"http", "https"}),
        allowed_hosts=frozenset({"api.example", "127.0.0.1", "0177.0.0.1"}),
    )
    with pytest.raises(EgressError) as caught:
        policy.require(raw, resolver=lambda _host: ("127.0.0.1",))
    assert "secret" not in str(caught.value)
    assert raw not in str(caught.value)


def test_denied_decision_and_repr_do_not_expose_credentials_or_addresses() -> None:
    policy = EgressPolicy(allowed_hosts=frozenset({"api.example"}))
    denied = policy.decide(
        "https://user:super-secret@api.example/private?token=also-secret",
        resolver=lambda _host: ("10.0.0.7",),
    )
    assert denied.reason == "userinfo_denied"
    assert denied.url == ""
    assert "secret" not in repr(denied)
    assert "10.0.0.7" not in repr(denied)


def test_egress_decision_carries_all_transport_constraints() -> None:
    policy = EgressPolicy(
        allowed_hosts=frozenset({"api.example"}),
        connect_deadline_seconds=2.5,
        read_deadline_seconds=3.5,
        total_deadline_seconds=4.5,
        response_budget_bytes=4,
        decompressed_budget_bytes=8,
        max_decompression_ratio=3,
        expected_content_types=frozenset({"application/json"}),
    )
    decision = policy.require("https://API.EXAMPLE/v1#fragment", resolver=_public_resolver)
    assert decision.url == "https://api.example/v1"
    assert decision.connect_deadline_seconds == 2.5
    assert decision.read_deadline_seconds == 3.5
    assert decision.total_deadline_seconds == 4.5
    assert decision.response_budget_bytes == 4
    assert decision.decompressed_budget_bytes == 8
    assert decision.expected_content_types == frozenset({"application/json"})
    assert bounded_response([b"ab", b"cd"], budget_bytes=4) == b"abcd"
    with pytest.raises(EgressError, match="budget"):
        bounded_response([b"abc", b"de"], budget_bytes=4)


def test_injected_transport_cannot_bypass_policy_or_peer_binding() -> None:
    policy = EgressPolicy(allowed_hosts=frozenset({"api.example"}))
    transport = _ScriptedTransport(_response(peer="1.1.1.1"))
    with pytest.raises(EgressError, match="connected_address_mismatch"):
        fetch_with_policy(
            "https://api.example/v1",
            policy=policy,
            transport=transport,
            resolver=_public_resolver,
        )
    assert transport.decisions[0].resolved_addresses == ("8.8.8.8",)

    never_called = _ScriptedTransport(_response())
    with pytest.raises(EgressError, match="host_denied"):
        fetch_with_policy(
            "https://evil.example/v1",
            policy=policy,
            transport=never_called,
            resolver=_public_resolver,
        )
    assert never_called.decisions == []


def test_redirects_re_resolve_each_hop_and_share_the_redirect_limit() -> None:
    resolved: list[str] = []

    def resolver(host: str) -> tuple[str, ...]:
        resolved.append(host)
        return {"one.example": ("8.8.8.8",), "two.example": ("1.1.1.1",)}[host]

    closed: list[str] = []
    transport = _ScriptedTransport(
        _response(
            status=302,
            headers={"location": "https://two.example/final"},
            close=lambda: closed.append("redirect"),
        ),
        _response(b"done", peer="1.1.1.1"),
    )
    result = fetch_with_policy(
        "https://one.example/start",
        policy=EgressPolicy(
            allowed_hosts=frozenset({"one.example", "two.example"}), max_redirects=1
        ),
        transport=transport,
        resolver=resolver,
    )
    assert result == b"done"
    assert resolved == ["one.example", "two.example"]
    assert [decision.hop for decision in transport.decisions] == [0, 1]
    assert closed == ["redirect"]

    with pytest.raises(EgressError, match="max_redirects_exceeded"):
        fetch_with_policy(
            "https://one.example/start",
            policy=EgressPolicy(allowed_hosts=frozenset({"one.example"}), max_redirects=0),
            transport=_ScriptedTransport(_response(status=302, headers={"location": "/again"})),
            resolver=lambda _host: ("8.8.8.8",),
        )


def test_redirect_to_private_resolution_is_denied_before_second_request() -> None:
    transport = _ScriptedTransport(
        _response(status=302, headers={"location": "https://private.example/x"})
    )

    def resolver(host: str) -> tuple[str, ...]:
        return ("127.0.0.1",) if host == "private.example" else ("8.8.8.8",)

    with pytest.raises(EgressError, match="private_address_denied"):
        fetch_with_policy(
            "https://public.example/x",
            policy=EgressPolicy(allowed_hosts=frozenset({"public.example", "private.example"})),
            transport=transport,
            resolver=resolver,
        )
    assert len(transport.decisions) == 1


def test_retries_are_bounded_and_preserve_total_policy_state() -> None:
    transport = _ScriptedTransport(
        EgressTransportError("transport_failure", retryable=True), _response(b"retried")
    )
    assert (
        fetch_with_policy(
            "https://api.example/x",
            policy=EgressPolicy(allowed_hosts=frozenset({"api.example"}), max_attempts_per_hop=2),
            transport=transport,
            resolver=_public_resolver,
        )
        == b"retried"
    )
    assert [decision.attempt for decision in transport.decisions] == [0, 1]


def test_response_content_type_encoded_and_decoded_budgets() -> None:
    json_policy = EgressPolicy(
        allowed_hosts=frozenset({"api.example"}),
        expected_content_types=frozenset({"application/json"}),
        response_budget_bytes=64,
        decompressed_budget_bytes=64,
    )
    with pytest.raises(EgressError, match="content_type_denied"):
        fetch_with_policy(
            "https://api.example/x",
            policy=json_policy,
            transport=_ScriptedTransport(_response(headers={"content-type": "text/html"})),
            resolver=_public_resolver,
        )
    with pytest.raises(EgressError, match="response_budget_exceeded"):
        fetch_with_policy(
            "https://api.example/x",
            policy=json_policy,
            transport=_ScriptedTransport(
                _response(headers={"content-type": "application/json", "content-length": "65"})
            ),
            resolver=_public_resolver,
        )

    bomb = gzip.compress(b"A" * 10_000)
    with pytest.raises(EgressError, match="decompression_(ratio|budget)_exceeded"):
        fetch_with_policy(
            "https://api.example/x",
            policy=EgressPolicy(
                allowed_hosts=frozenset({"api.example"}),
                response_budget_bytes=len(bomb) + 1,
                decompressed_budget_bytes=20_000,
                max_decompression_ratio=10,
            ),
            transport=_ScriptedTransport(_response(bomb, headers={"content-encoding": "gzip"})),
            resolver=_public_resolver,
        )

    compressed = gzip.compress(b'{"ok":true}')
    assert (
        fetch_with_policy(
            "https://api.example/x",
            policy=EgressPolicy(
                allowed_hosts=frozenset({"api.example"}),
                response_budget_bytes=64,
                decompressed_budget_bytes=64,
            ),
            transport=_ScriptedTransport(
                _response(compressed, headers={"content-encoding": "gzip"})
            ),
            resolver=_public_resolver,
        )
        == b'{"ok":true}'
    )


def test_proxy_only_policy_requires_the_validated_proxy_peer() -> None:
    def resolver(host: str) -> tuple[str, ...]:
        return ("9.9.9.9",) if host == "proxy.example" else ("8.8.8.8",)

    policy = EgressPolicy(
        allowed_hosts=frozenset({"api.example"}), proxy_url="http://proxy.example:8080"
    )
    for response in (
        _response(peer="8.8.8.8"),
        _response(peer="8.8.8.8", via_proxy=True),
    ):
        with pytest.raises(EgressError, match="(proxy_route|connected_address)_mismatch"):
            fetch_with_policy(
                "https://api.example/x",
                policy=policy,
                transport=_ScriptedTransport(response),
                resolver=resolver,
            )
    assert (
        fetch_with_policy(
            "https://api.example/x",
            policy=policy,
            transport=_ScriptedTransport(_response(peer="9.9.9.9", via_proxy=True)),
            resolver=resolver,
        )
        == b"ok"
    )


def test_request_budget_is_cumulative_and_transport_errors_are_redacted() -> None:
    budget = RequestBudget(RequestBudgetLimits(response_bytes=3, decompressed_bytes=3))
    token = set_request_budget(budget)
    try:
        with pytest.raises(EgressError, match="request_budget_exceeded"):
            fetch_with_policy(
                "https://api.example/x",
                policy=EgressPolicy(allowed_hosts=frozenset({"api.example"})),
                transport=_ScriptedTransport(_response([b"ab", b"cd"])),
                resolver=_public_resolver,
            )
        assert budget.used("response_bytes") == 2
    finally:
        reset_request_budget(token)

    for failure in (
        RuntimeError("token=super-secret"),
        EgressTransportError("token=super-secret"),
    ):
        with pytest.raises(EgressError) as caught:
            fetch_with_policy(
                "https://api.example/x",
                policy=EgressPolicy(allowed_hosts=frozenset({"api.example"})),
                transport=_ScriptedTransport(failure),
                resolver=_public_resolver,
            )
        assert str(caught.value) == "egress denied: transport_failure"


def test_read_and_total_deadlines_are_enforced_outside_the_transport() -> None:
    now = [0.0]

    def clock() -> float:
        return now[0]

    def delayed_body() -> Iterable[bytes]:
        yield b"a"
        now[0] = 3.0
        yield b"b"

    with pytest.raises(EgressError, match="read_deadline_exceeded"):
        fetch_with_policy(
            "https://api.example/x",
            policy=EgressPolicy(
                allowed_hosts=frozenset({"api.example"}),
                connect_deadline_seconds=1,
                read_deadline_seconds=2,
                total_deadline_seconds=5,
            ),
            transport=_ScriptedTransport(_response(delayed_body())),
            resolver=_public_resolver,
            clock=clock,
        )


def test_compatibility_validator_still_denies_private_targets() -> None:
    with pytest.raises(EgressError, match="private_address_denied"):
        assert_ssrf_safe("http://127.0.0.1/admin")
