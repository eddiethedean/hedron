"""Async bridge, cache-key, and connection-bound HTTP transport coverage."""

from __future__ import annotations

import asyncio
import http.client
from typing import ClassVar

import pytest

from hedron_core.async_bridge import run_coro, run_prepare, running_loop
from hedron_core.cache.keying import build_cache_key
from hedron_core.egress import EgressDecision, EgressDecisionKind, EgressTransportError
from hedron_core.egress_http import (
    StdlibEgressTransport,
    _address_for_attempt,
    _authority,
    _PinnedHTTPSConnection,
    _response_headers,
)
from hedron_core.security import Secret


async def _answer(value: int) -> int:
    await asyncio.sleep(0)
    return value


def test_async_bridge_runs_coroutines_and_prepare_factories_without_a_loop() -> None:
    prepared: list[str] = []

    async def prepare() -> None:
        prepared.append("ready")

    assert running_loop() is False
    assert run_coro(_answer(42)) == 42
    run_prepare(prepare)
    assert prepared == ["ready"]


def test_async_bridge_rejects_nested_loop_and_closes_created_coroutine() -> None:
    prepared: list[str] = []

    async def scenario() -> None:
        assert running_loop() is True
        coroutine = _answer(1)
        with pytest.raises(RuntimeError, match="already running"):
            run_coro(coroutine)
        assert coroutine.cr_frame is None

        async def prepare() -> None:
            prepared.append("called")

        with pytest.raises(RuntimeError, match="prepare_tree"):
            run_prepare(prepare)

    asyncio.run(scenario())
    assert prepared == []


def test_cache_keys_are_order_independent_but_contract_sensitive() -> None:
    first = build_cache_key(
        identity="items:list",
        args=({"b": 2, "a": 1},),
        kwargs={"limit": 10, "filters": ["a", "b"]},
        vary={"tenant": "one"},
    )
    reordered = build_cache_key(
        identity="items:list",
        args=({"a": 1, "b": 2},),
        kwargs={"filters": ("a", "b"), "limit": 10},
        vary={"tenant": "one"},
    )
    changed = build_cache_key(
        identity="items:list",
        args=({"a": 1, "b": 2},),
        kwargs={"filters": ("a", "b"), "limit": 10},
        vary={"tenant": "two"},
    )
    assert first == reordered
    assert first != changed
    assert len(first) == 24


def test_cache_keys_hash_secrets_and_support_models_and_repr_fallback() -> None:
    class Model:
        def model_dump(self) -> object:
            return {"id": 1}

    class Stable:
        def __repr__(self) -> str:
            return "Stable(value=1)"

    secret = "never-emit-this-secret"
    key = build_cache_key(
        identity="secure",
        args=(Secret(secret), Model(), Stable(), {2: "two"}),
    )
    assert secret not in key
    assert key == build_cache_key(
        identity="secure",
        args=(Secret(secret), Model(), Stable(), {2: "two"}),
    )


@pytest.mark.parametrize("value", [type("Request", (), {})(), type("HTTPConnection", (), {})()])
def test_cache_keys_reject_request_objects(value: object) -> None:
    with pytest.raises(ValueError, match="cache key argument"):
        build_cache_key(identity="unsafe", args=(value,))


def test_cache_keys_reject_dependency_objects() -> None:
    class DatabaseDependency:
        pass

    with pytest.raises(ValueError, match="DatabaseDependency"):
        build_cache_key(identity="unsafe", args=(DatabaseDependency(),))


class _Socket:
    def __init__(self) -> None:
        self.timeout: float | None = None

    def getpeername(self) -> tuple[str, int]:
        return ("203.0.113.10", 443)

    def settimeout(self, value: float) -> None:
        self.timeout = value


class _Response:
    status = 200

    def __init__(
        self,
        chunks: list[bytes] | None = None,
        headers: list[tuple[str, str]] | None = None,
        read_error: bool = False,
    ) -> None:
        self.chunks = list(chunks or [b"one", b"two", b""])
        self.headers = headers or [("Content-Type", "text/plain"), ("X-Test", "one")]
        self.read_error = read_error
        self.closed = False

    def getheaders(self) -> list[tuple[str, str]]:
        return self.headers

    def read(self, size: int) -> bytes:
        assert size > 0
        if self.read_error:
            raise OSError("read failed")
        return self.chunks.pop(0)

    def close(self) -> None:
        self.closed = True


class _Connection:
    instances: ClassVar[list[_Connection]] = []
    response_factory = staticmethod(_Response)
    request_error: BaseException | None = None

    def __init__(self, host: str, port: int, *, timeout: float) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock: _Socket | None = _Socket()
        self.closed = False
        self.request_args: tuple[object, ...] | None = None
        self.response = self.response_factory()
        self.instances.append(self)

    def request(self, *args: object, **kwargs: object) -> None:
        if self.request_error is not None:
            raise self.request_error
        self.request_args = (*args, kwargs)

    def getresponse(self) -> _Response:
        return self.response

    def close(self) -> None:
        self.closed = True


def _decision(**changes: object) -> EgressDecision:
    values: dict[str, object] = {
        "kind": EgressDecisionKind.ALLOW,
        "url": "http://example.test:8080/path?q=1",
        "resolved_addresses": ("203.0.113.10", "203.0.113.11"),
        "connect_deadline_seconds": 2.0,
        "scheme": "http",
        "host": "example.test",
        "port": 8080,
        "read_deadline_seconds": 3.0,
        "attempt": 0,
    }
    values.update(changes)
    return EgressDecision(**values)  # type: ignore[arg-type]


def test_egress_transport_reads_stream_and_closes_resources(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _Connection.instances.clear()
    _Connection.request_error = None
    _Connection.response_factory = staticmethod(_Response)
    monkeypatch.setattr(http.client, "HTTPConnection", _Connection)

    response = StdlibEgressTransport(chunk_size=3, user_agent="tests/1").request(
        decision=_decision()
    )
    connection = _Connection.instances[-1]

    assert response.status_code == 200
    assert response.headers == {"content-type": "text/plain", "x-test": "one"}
    assert response.connected_address == "203.0.113.10"
    assert response.via_proxy is False
    assert list(response.body) == [b"one", b"two"]
    assert connection.request_args == (
        "GET",
        "/path?q=1",
        {
            "headers": {
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "close",
                "Host": "example.test:8080",
                "User-Agent": "tests/1",
            },
            "encode_chunked": False,
        },
    )
    assert connection.response.closed is True
    assert connection.closed is True


def test_egress_transport_http_proxy_uses_absolute_target(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _Connection.instances.clear()
    _Connection.request_error = None
    monkeypatch.setattr(http.client, "HTTPConnection", _Connection)
    decision = _decision(
        proxy_url="http://proxy.test:3128",
        proxy_resolved_addresses=("198.51.100.4",),
    )

    response = StdlibEgressTransport().request(decision=decision)
    connection = _Connection.instances[-1]

    assert response.via_proxy is True
    assert connection.host == "198.51.100.4"
    assert connection.port == 3128
    assert connection.request_args is not None
    assert connection.request_args[1] == decision.url
    response.close()
    assert connection.closed is True


@pytest.mark.parametrize("chunk_size", [0, -1, True, 1.5])
def test_egress_transport_validates_chunk_size(chunk_size: object) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        StdlibEgressTransport(chunk_size=chunk_size)  # type: ignore[arg-type]


def test_egress_transport_requires_resolved_target_and_proxy() -> None:
    transport = StdlibEgressTransport()
    with pytest.raises(EgressTransportError, match="dns_unresolved"):
        transport.request(decision=_decision(resolved_addresses=()))
    with pytest.raises(EgressTransportError, match="proxy_dns_unresolved"):
        transport.request(decision=_decision(proxy_url="http://proxy.test"))


def test_egress_transport_wraps_request_and_read_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _Connection.instances.clear()
    _Connection.request_error = OSError("connect failed")
    monkeypatch.setattr(http.client, "HTTPConnection", _Connection)
    with pytest.raises(EgressTransportError, match="transport_failure") as request_error:
        StdlibEgressTransport().request(decision=_decision())
    assert request_error.value.retryable is True
    assert _Connection.instances[-1].closed is True

    _Connection.request_error = None
    _Connection.response_factory = staticmethod(lambda: _Response(read_error=True))
    response = StdlibEgressTransport().request(decision=_decision())
    with pytest.raises(EgressTransportError, match="transport_read_failure"):
        list(response.body)
    assert _Connection.instances[-1].closed is True
    assert _Connection.instances[-1].response.closed is True


def test_egress_transport_rejects_missing_peer_and_conflicting_singletons(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class NoPeerConnection(_Connection):
        def __init__(self, host: str, port: int, *, timeout: float) -> None:
            super().__init__(host, port, timeout=timeout)
            self.sock = None

    monkeypatch.setattr(http.client, "HTTPConnection", NoPeerConnection)
    with pytest.raises(EgressTransportError, match="transport_peer_unavailable"):
        StdlibEgressTransport().request(decision=_decision())

    _Connection.response_factory = staticmethod(
        lambda: _Response(headers=[("Content-Length", "1"), ("content-length", "2")])
    )
    monkeypatch.setattr(http.client, "HTTPConnection", _Connection)
    with pytest.raises(EgressTransportError, match="conflicting_response_headers"):
        StdlibEgressTransport().request(decision=_decision())


def test_egress_address_authority_and_header_helpers() -> None:
    assert _address_for_attempt(("a", "b"), 3) == "b"
    assert _authority("example.test", 443, "https") == "example.test"
    assert _authority("2001:db8::1", 8443, "https") == "[2001:db8::1]:8443"
    response = _Response(headers=[("X-Test", " one "), ("x-test", "two")])
    assert _response_headers(response) == {"x-test": "two"}  # type: ignore[arg-type]


def test_pinned_https_connection_uses_validated_address_and_sni(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    connected: list[tuple[tuple[str, int], float]] = []
    wrapped: list[tuple[object, str]] = []
    sock = _Socket()

    class Context:
        def wrap_socket(self, raw: object, *, server_hostname: str) -> object:
            wrapped.append((raw, server_hostname))
            return raw

    def create_connection(address: tuple[str, int], timeout: float) -> _Socket:
        connected.append((address, timeout))
        return sock

    monkeypatch.setattr("hedron_core.egress_http.socket.create_connection", create_connection)
    connection = _PinnedHTTPSConnection(
        "example.test",
        "203.0.113.9",
        443,
        timeout=4.0,
        context=Context(),  # type: ignore[arg-type]
    )
    connection.connect()

    assert connected == [(("203.0.113.9", 443), 4.0)]
    assert wrapped == [(sock, "example.test")]
