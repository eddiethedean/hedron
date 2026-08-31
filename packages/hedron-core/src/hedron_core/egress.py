"""Deny-by-default outbound egress and SSRF enforcement (EGRESS-056)."""

from __future__ import annotations

import ipaddress
import math
import re
import socket
import time
import zlib
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field, replace
from typing import Any, NoReturn, Protocol, cast
from urllib.parse import SplitResult, urljoin, urlsplit, urlunsplit

from hedron_core.compat import StrEnum

_REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})
_HTTP_SCHEMES = frozenset({"http", "https"})
_SENSITIVE_HEADER_KEYS = frozenset({"authorization", "cookie", "proxy-authorization", "set-cookie"})
_HEADER_NAME = re.compile(r"^[!#$%&'*+.^_`|~0-9A-Za-z-]+$")
_TRANSPORT_REASONS = frozenset(
    {
        "conflicting_response_headers",
        "dns_unresolved",
        "proxy_dns_unresolved",
        "transport_failure",
        "transport_peer_unavailable",
        "transport_read_failure",
    }
)


class EgressDecisionKind(StrEnum):
    ALLOW = "allow"
    DENY = "deny"


class EgressError(ValueError):
    """Raised when outbound egress fails closed."""


class EgressTransportError(EgressError):
    """Redacted transport failure with an explicit retry disposition."""

    def __init__(self, reason: str = "transport_failure", *, retryable: bool = False) -> None:
        self.reason = _transport_reason(reason)
        self.retryable = retryable
        super().__init__(f"egress denied: {self.reason}")


class SecurityEgressPolicy(Protocol):
    """Security-policy fields needed to derive an egress policy."""

    egress_allow_hosts: frozenset[str]
    egress_deny_by_default: bool


@dataclass(frozen=True, slots=True)
class EgressDecision:
    kind: EgressDecisionKind
    url: str = field(repr=False)
    reason: str = ""
    resolved_addresses: tuple[str, ...] = field(default=(), repr=False)
    hop: int = 0
    connect_deadline_seconds: float = 0.0
    response_budget_bytes: int = 0
    scheme: str = ""
    host: str = ""
    port: int = 0
    origin: str = ""
    read_deadline_seconds: float = 0.0
    total_deadline_seconds: float = 0.0
    decompressed_budget_bytes: int = 0
    max_decompression_ratio: float = 0.0
    expected_content_types: frozenset[str] = field(default_factory=frozenset[str])
    proxy_url: str | None = None
    proxy_resolved_addresses: tuple[str, ...] = field(default=(), repr=False)
    attempt: int = 0


@dataclass(slots=True)
class EgressResponse:
    """Transport result whose observed peer is revalidated by the core."""

    status_code: int
    headers: Mapping[str, str] = field(repr=False)
    body: bytes | Iterable[bytes] = field(repr=False)
    connected_address: str = field(repr=False)
    via_proxy: bool = False
    close: Callable[[], None] = field(default=lambda: None, repr=False)


class EgressTransport(Protocol):
    """Injected transport that reports the peer used for each request.

    A transport must not follow redirects or decompress the response. The core
    owns those operations so injected implementations cannot reset policy or
    budget state between hops.
    """

    def request(self, *, decision: EgressDecision) -> EgressResponse: ...


class _Decompressor(Protocol):
    @property
    def eof(self) -> bool: ...

    @property
    def unconsumed_tail(self) -> bytes: ...

    @property
    def unused_data(self) -> bytes: ...

    def decompress(self, data: bytes, max_length: int = 0) -> bytes: ...

    def flush(self, length: int = ...) -> bytes: ...


@dataclass(frozen=True, slots=True)
class EgressPolicy:
    """Transport-neutral egress policy with connection-bound enforcement."""

    version: int = 1
    allowed_schemes: frozenset[str] = field(default_factory=lambda: frozenset({"https"}))
    allowed_hosts: frozenset[str] = field(default_factory=frozenset[str])
    allowed_origins: frozenset[str] = field(default_factory=frozenset[str])
    allowed_ports: frozenset[int] = field(default_factory=lambda: frozenset({443, 80}))
    allow_private_addresses: bool = False
    max_redirects: int = 3
    max_attempts_per_hop: int = 1
    connect_deadline_seconds: float = 5.0
    read_deadline_seconds: float = 10.0
    total_deadline_seconds: float = 30.0
    response_budget_bytes: int = 1_048_576
    decompressed_budget_bytes: int = 4_194_304
    max_decompression_ratio: float = 20.0
    expected_content_types: frozenset[str] = field(default_factory=frozenset[str])
    proxy_url: str | None = None
    allow_private_proxy_addresses: bool = False
    deny_by_default: bool = True

    def __post_init__(self) -> None:
        _positive_int("max_attempts_per_hop", self.max_attempts_per_hop)
        _positive_int("response_budget_bytes", self.response_budget_bytes)
        _positive_int("decompressed_budget_bytes", self.decompressed_budget_bytes)
        max_redirects = cast(Any, self.max_redirects)
        if (
            isinstance(max_redirects, bool)
            or not isinstance(max_redirects, int)
            or max_redirects < 0
        ):
            raise ValueError("max_redirects must be a non-negative integer")
        _positive_finite("connect_deadline_seconds", self.connect_deadline_seconds)
        _positive_finite("read_deadline_seconds", self.read_deadline_seconds)
        _positive_finite("total_deadline_seconds", self.total_deadline_seconds)
        _positive_finite("max_decompression_ratio", self.max_decompression_ratio)
        if self.total_deadline_seconds < self.connect_deadline_seconds:
            raise ValueError("total_deadline_seconds must be >= connect_deadline_seconds")
        if self.total_deadline_seconds < self.read_deadline_seconds:
            raise ValueError("total_deadline_seconds must be >= read_deadline_seconds")
        schemes = frozenset(str(item).lower() for item in self.allowed_schemes)
        if not schemes or not schemes.issubset(_HTTP_SCHEMES):
            raise ValueError("allowed_schemes must contain only http and/or https")
        raw_ports = cast(Any, self.allowed_ports)
        if not isinstance(raw_ports, frozenset):
            raise ValueError("allowed_ports must contain integers from 1 through 65535")
        ports = cast(frozenset[object], raw_ports)
        if any(
            isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65_535
            for port in ports
        ):
            raise ValueError("allowed_ports must contain integers from 1 through 65535")
        content_types = frozenset(
            _normalize_content_type(item) for item in self.expected_content_types
        )
        if "" in content_types:
            raise ValueError("expected_content_types entries must be non-empty MIME types")
        object.__setattr__(self, "allowed_schemes", schemes)
        object.__setattr__(
            self, "allowed_hosts", frozenset(_normalize_host(h) for h in self.allowed_hosts)
        )
        object.__setattr__(
            self,
            "allowed_origins",
            frozenset(_canonical_configured_origin(item) for item in self.allowed_origins),
        )
        object.__setattr__(self, "expected_content_types", content_types)
        if self.proxy_url is not None:
            proxy = _parse_http_url(self.proxy_url)
            if proxy is None or proxy.scheme.lower() != "http":
                raise ValueError("proxy_url must be an absolute http URL without credentials")
            if proxy.username or proxy.password or proxy.path not in {"", "/"}:
                raise ValueError("proxy_url must not contain credentials or a path")
            object.__setattr__(self, "proxy_url", _url_without_fragment(proxy))

    def decide(
        self,
        url: str,
        *,
        hop: int = 0,
        resolver: Callable[[str], tuple[str, ...]] | None = None,
    ) -> EgressDecision:
        if hop > self.max_redirects:
            return _deny(url, "max_redirects_exceeded", hop)
        parsed = _parse_http_url(url)
        if parsed is None:
            return _deny(url, "invalid_url", hop)
        scheme = parsed.scheme.lower()
        if scheme not in self.allowed_schemes:
            return _deny(url, "scheme_denied", hop)
        host = _normalize_host(parsed.hostname or "")
        if not host:
            return _deny(url, "missing_host", hop)
        if parsed.username or parsed.password:
            return _deny(url, "userinfo_denied", hop)
        if self.deny_by_default and host not in self.allowed_hosts:
            return _deny(url, "host_denied", hop)
        port = parsed.port if parsed.port is not None else _default_port(scheme)
        if port not in self.allowed_ports:
            return _deny(url, "port_denied", hop)
        origin = _canonical_origin(scheme, host, port)
        if self.allowed_origins and origin not in self.allowed_origins:
            return _deny(url, "origin_denied", hop)
        addresses, reason = _resolve_addresses(
            host,
            resolver=resolver,
            allow_private=self.allow_private_addresses,
        )
        if reason:
            return _deny(url, reason, hop, addresses=addresses)

        proxy_addresses: tuple[str, ...] = ()
        if self.proxy_url is not None:
            proxy = cast(SplitResult, _parse_http_url(self.proxy_url))
            proxy_host = _normalize_host(proxy.hostname or "")
            proxy_addresses, reason = _resolve_addresses(
                proxy_host,
                resolver=resolver,
                allow_private=self.allow_private_proxy_addresses,
            )
            if reason:
                return _deny(url, f"proxy_{reason}", hop, addresses=proxy_addresses)

        return EgressDecision(
            kind=EgressDecisionKind.ALLOW,
            url=_canonical_url(parsed, scheme=scheme, host=host, port=port),
            reason="allowed",
            resolved_addresses=addresses,
            hop=hop,
            connect_deadline_seconds=float(self.connect_deadline_seconds),
            response_budget_bytes=self.response_budget_bytes,
            scheme=scheme,
            host=host,
            port=port,
            origin=origin,
            read_deadline_seconds=float(self.read_deadline_seconds),
            total_deadline_seconds=float(self.total_deadline_seconds),
            decompressed_budget_bytes=self.decompressed_budget_bytes,
            max_decompression_ratio=float(self.max_decompression_ratio),
            expected_content_types=self.expected_content_types,
            proxy_url=self.proxy_url,
            proxy_resolved_addresses=proxy_addresses,
        )

    def require(
        self,
        url: str,
        *,
        hop: int = 0,
        resolver: Callable[[str], tuple[str, ...]] | None = None,
    ) -> EgressDecision:
        decision = self.decide(url, hop=hop, resolver=resolver)
        if decision.kind is EgressDecisionKind.DENY:
            _raise_denied(decision.reason, hop=hop)
        return decision


def _positive_int(name: str, value: object) -> None:
    raw = cast(Any, value)
    if isinstance(raw, bool) or not isinstance(raw, int) or raw < 1:
        raise ValueError(f"{name} must be a positive integer")


def _positive_finite(name: str, value: object) -> None:
    raw = cast(Any, value)
    if (
        isinstance(raw, bool)
        or not isinstance(raw, (int, float))
        or not math.isfinite(float(raw))
        or raw <= 0
    ):
        raise ValueError(f"{name} must be finite and > 0")


def _deny(
    url: str,
    reason: str,
    hop: int,
    *,
    addresses: tuple[str, ...] = (),
) -> EgressDecision:
    return EgressDecision(
        kind=EgressDecisionKind.DENY,
        url="",
        reason=reason,
        hop=hop,
    )


def _raise_denied(reason: str, *, hop: int) -> NoReturn:
    from hedron_core.security_events import SecurityEvent, emit_security_event

    emit_security_event(SecurityEvent(code="egress.denied", detail={"reason": reason, "hop": hop}))
    raise EgressError(f"egress denied: {reason}")


def _transport_reason(reason: str) -> str:
    return reason if reason in _TRANSPORT_REASONS else "transport_failure"


def _normalize_host(host: str) -> str:
    raw = str(host).strip().lower().rstrip(".")
    if not raw or "%" in raw or any(ord(char) < 33 for char in raw):
        return ""
    try:
        return ipaddress.ip_address(raw).compressed
    except ValueError:
        try:
            return raw.encode("idna").decode("ascii")
        except UnicodeError:
            return ""


def _parse_http_url(url: str) -> SplitResult | None:
    raw = cast(Any, url)
    if not isinstance(raw, str) or not raw or "\\" in raw:
        return None
    if any(ord(char) < 32 or ord(char) == 127 for char in raw):
        return None
    try:
        parsed = urlsplit(raw)
        _ = parsed.port
    except ValueError:
        return None
    if parsed.scheme.lower() not in _HTTP_SCHEMES or not parsed.netloc or not parsed.hostname:
        return None
    return parsed


def _default_port(scheme: str) -> int:
    return 443 if scheme == "https" else 80


def _authority(host: str, port: int, scheme: str) -> str:
    display_host = f"[{host}]" if ":" in host else host
    if port == _default_port(scheme):
        return display_host
    return f"{display_host}:{port}"


def _canonical_origin(scheme: str, host: str, port: int) -> str:
    return f"{scheme}://{_authority(host, port, scheme)}"


def _canonical_configured_origin(origin: str) -> str:
    parsed = _parse_http_url(origin)
    if parsed is None or parsed.username or parsed.password:
        raise ValueError(f"invalid allowed origin: {origin!r}")
    scheme = parsed.scheme.lower()
    host = _normalize_host(parsed.hostname or "")
    port = parsed.port if parsed.port is not None else _default_port(scheme)
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise ValueError(f"allowed origin must not contain path/query/fragment: {origin!r}")
    return _canonical_origin(scheme, host, port)


def _url_without_fragment(parsed: SplitResult) -> str:
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path or "/", parsed.query, ""))


def _canonical_url(parsed: SplitResult, *, scheme: str, host: str, port: int) -> str:
    return urlunsplit(
        (scheme, _authority(host, port, scheme), parsed.path or "/", parsed.query, "")
    )


def _normalize_address(address: str) -> str:
    raw = str(address).split("%", 1)[0]
    try:
        return ipaddress.ip_address(raw).compressed
    except ValueError:
        return ""


def _resolve_addresses(
    host: str,
    *,
    resolver: Callable[[str], tuple[str, ...]] | None,
    allow_private: bool,
) -> tuple[tuple[str, ...], str]:
    try:
        raw_addresses = (resolver or default_resolve)(host)
    except OSError:
        return (), "dns_resolution_failed"
    addresses = tuple(
        dict.fromkeys(
            normalized for item in raw_addresses if (normalized := _normalize_address(item))
        )
    )
    if not addresses:
        return (), "dns_unresolved"
    if not allow_private and any(_is_blocked_address(address) for address in addresses):
        return addresses, "private_address_denied"
    return addresses, ""


def _normalize_content_type(value: object) -> str:
    return str(value).split(";", 1)[0].strip().lower()


def _normalized_headers(headers: Mapping[str, str], *, hop: int) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for raw_name, raw_value in headers.items():
        name = str(raw_name).strip().lower()
        value = str(raw_value).strip()
        if not _HEADER_NAME.fullmatch(name) or any(
            ord(char) < 32 or ord(char) == 127 for char in value
        ):
            _raise_denied("invalid_response_headers", hop=hop)
        if name in _SENSITIVE_HEADER_KEYS:
            # Headers remain available to the internal policy engine only and
            # are never included in diagnostics. Keeping the branch explicit
            # prevents future logging code from treating the mapping as safe.
            normalized[name] = value
        else:
            normalized[name] = value
    return normalized


def _verified_peer(response: EgressResponse, decision: EgressDecision) -> None:
    peer = _normalize_address(response.connected_address)
    expected_proxy = decision.proxy_url is not None
    if response.via_proxy is not expected_proxy:
        _raise_denied("proxy_route_mismatch", hop=decision.hop)
    approved = decision.proxy_resolved_addresses if expected_proxy else decision.resolved_addresses
    if not peer or peer not in approved:
        _raise_denied("connected_address_mismatch", hop=decision.hop)


def _charge_request_budget(dimension: str, amount: int, *, hop: int) -> None:
    from hedron_core.request_budget import BudgetExceeded, get_request_budget

    budget = get_request_budget()
    if budget is None:
        return
    try:
        budget.charge(dimension, amount)
    except BudgetExceeded:
        _raise_denied("request_budget_exceeded", hop=hop)


def _decoded_chunks(
    chunks: Iterable[bytes],
    *,
    content_encoding: str,
    decision: EgressDecision,
    started: float,
    clock: Callable[[], float],
) -> Iterable[bytes]:
    encoding = content_encoding.strip().lower()
    if encoding in {"", "identity"}:
        decoder: _Decompressor | None = None
    elif encoding == "gzip":
        decoder = cast(_Decompressor, zlib.decompressobj(16 + zlib.MAX_WBITS))
    elif encoding == "deflate":
        decoder = cast(_Decompressor, zlib.decompressobj())
    else:
        _raise_denied("content_encoding_denied", hop=decision.hop)
    encoded = 0
    decoded = 0
    last_chunk_at = clock()
    for raw_chunk in chunks:
        now = clock()
        if now - started > decision.total_deadline_seconds:
            _raise_denied("total_deadline_exceeded", hop=decision.hop)
        if now - last_chunk_at > decision.read_deadline_seconds:
            _raise_denied("read_deadline_exceeded", hop=decision.hop)
        last_chunk_at = now
        checked = _as_bytes(cast(Any, raw_chunk))
        if checked is None:
            _raise_denied("non_byte_response_chunk", hop=decision.hop)
        if len(checked) > decision.response_budget_bytes - encoded:
            _raise_denied("response_budget_exceeded", hop=decision.hop)
        encoded += len(checked)
        _charge_request_budget("response_bytes", len(checked), hop=decision.hop)
        if decoder is None:
            output = checked
            decoded = _validate_decoded_size(
                output,
                encoded=encoded,
                decoded=decoded,
                decision=decision,
            )
            yield output
        else:
            pending = checked
            while pending:
                allowance = _decoded_allowance(
                    encoded=encoded,
                    decoded=decoded,
                    decision=decision,
                )
                try:
                    output = decoder.decompress(pending, max(1, allowance + 1))
                except zlib.error:
                    _raise_denied("invalid_compressed_response", hop=decision.hop)
                if decoder.unused_data:
                    _raise_denied("invalid_compressed_response", hop=decision.hop)
                next_pending = decoder.unconsumed_tail
                if output:
                    decoded = _validate_decoded_size(
                        output,
                        encoded=encoded,
                        decoded=decoded,
                        decision=decision,
                    )
                    yield output
                if next_pending == pending:
                    _raise_denied("invalid_compressed_response", hop=decision.hop)
                pending = next_pending
    if decoder is not None:
        allowance = _decoded_allowance(
            encoded=encoded,
            decoded=decoded,
            decision=decision,
        )
        try:
            output = decoder.flush(max(1, allowance + 1))
        except zlib.error:
            _raise_denied("invalid_compressed_response", hop=decision.hop)
        if not decoder.eof:
            _raise_denied("truncated_compressed_response", hop=decision.hop)
        if output:
            _validate_decoded_size(
                output,
                encoded=encoded,
                decoded=decoded,
                decision=decision,
            )
            yield output


def _decoded_allowance(*, encoded: int, decoded: int, decision: EgressDecision) -> int:
    remaining_size = decision.decompressed_budget_bytes - decoded
    remaining_ratio = math.floor(decision.max_decompression_ratio * encoded) - decoded
    return max(0, min(remaining_size, remaining_ratio))


def _validate_decoded_size(
    output: bytes,
    *,
    encoded: int,
    decoded: int,
    decision: EgressDecision,
) -> int:
    next_decoded = decoded + len(output)
    if next_decoded > decision.decompressed_budget_bytes:
        _raise_denied("decompressed_budget_exceeded", hop=decision.hop)
    if next_decoded / max(1, encoded) > decision.max_decompression_ratio:
        _raise_denied("decompression_ratio_exceeded", hop=decision.hop)
    _charge_request_budget("decompressed_bytes", len(output), hop=decision.hop)
    return next_decoded


def bounded_response(chunks: Iterable[bytes], *, budget_bytes: int) -> bytes:
    """Compatibility collector that rejects before buffering an oversized chunk."""
    _positive_int("budget_bytes", budget_bytes)
    collected = bytearray()
    for chunk in chunks:
        checked = _as_bytes(cast(Any, chunk))
        if checked is None:
            raise EgressError("egress denied: non_byte_response_chunk")
        if len(checked) > budget_bytes - len(collected):
            raise EgressError("egress denied: response_budget_exceeded")
        collected.extend(checked)
    return bytes(collected)


def _as_bytes(value: Any) -> bytes | None:
    if isinstance(value, bytes):
        return value
    if isinstance(value, bytearray):
        return bytes(value)
    if isinstance(value, memoryview):
        return cast(memoryview[int], value).tobytes()
    return None


def fetch_with_policy(
    url: str,
    *,
    policy: EgressPolicy,
    transport: EgressTransport,
    resolver: Callable[[str], tuple[str, ...]] | None = None,
    clock: Callable[[], float] | None = None,
) -> bytes:
    """Fetch through a connection-bound, redirect-safe, cumulative policy path."""
    monotonic = clock or time.monotonic
    started = monotonic()
    current_url = url
    for hop in range(policy.max_redirects + 1):
        if monotonic() - started > policy.total_deadline_seconds:
            _raise_denied("total_deadline_exceeded", hop=hop)
        decision = policy.require(current_url, hop=hop, resolver=resolver)
        response: EgressResponse | None = None
        for attempt in range(policy.max_attempts_per_hop):
            elapsed = monotonic() - started
            if elapsed > policy.total_deadline_seconds:
                _raise_denied("total_deadline_exceeded", hop=hop)
            active = replace(
                decision,
                attempt=attempt,
                total_deadline_seconds=policy.total_deadline_seconds - elapsed,
                connect_deadline_seconds=min(
                    decision.connect_deadline_seconds,
                    policy.total_deadline_seconds - elapsed,
                ),
                read_deadline_seconds=min(
                    decision.read_deadline_seconds,
                    policy.total_deadline_seconds - elapsed,
                ),
            )
            try:
                response = transport.request(decision=active)
            except EgressTransportError as exc:
                if exc.retryable and attempt + 1 < policy.max_attempts_per_hop:
                    continue
                _raise_denied(_transport_reason(exc.reason), hop=hop)
            except OSError:
                if attempt + 1 < policy.max_attempts_per_hop:
                    continue
                _raise_denied("transport_failure", hop=hop)
            except Exception:  # noqa: BLE001 - untrusted transport boundary is redacted
                _raise_denied("transport_failure", hop=hop)
            break
        if response is None:
            _raise_denied("transport_failure", hop=hop)
        try:
            if monotonic() - started > policy.total_deadline_seconds:
                _raise_denied("total_deadline_exceeded", hop=hop)
            _verified_peer(response, decision)
            status = cast(Any, response.status_code)
            if isinstance(status, bool) or not isinstance(status, int) or not 100 <= status <= 599:
                _raise_denied("invalid_response_status", hop=hop)
            headers = _normalized_headers(response.headers, hop=hop)
            if status in _REDIRECT_STATUSES:
                location = headers.get("location")
                if not location:
                    _raise_denied("redirect_location_missing", hop=hop)
                if hop >= policy.max_redirects:
                    _raise_denied("max_redirects_exceeded", hop=hop + 1)
                current_url = urljoin(decision.url, location)
                continue
            content_type = _normalize_content_type(headers.get("content-type", ""))
            if (
                decision.expected_content_types
                and content_type not in decision.expected_content_types
            ):
                _raise_denied("content_type_denied", hop=hop)
            content_length = headers.get("content-length")
            if content_length is not None:
                try:
                    declared_length = int(content_length)
                except ValueError:
                    _raise_denied("invalid_content_length", hop=hop)
                if declared_length < 0 or declared_length > decision.response_budget_bytes:
                    _raise_denied("response_budget_exceeded", hop=hop)
            chunks: Iterable[bytes]
            raw_body = response.body
            if isinstance(raw_body, (bytes, bytearray, memoryview)):
                chunks = (bytes(raw_body),)
            else:
                chunks = raw_body
            decoded = _decoded_chunks(
                chunks,
                content_encoding=headers.get("content-encoding", ""),
                decision=decision,
                started=started,
                clock=monotonic,
            )
            try:
                return b"".join(decoded)
            except EgressTransportError as exc:
                _raise_denied(_transport_reason(exc.reason), hop=hop)
            except EgressError:
                raise
            except Exception:  # noqa: BLE001 - untrusted body iterator is redacted
                _raise_denied("transport_read_failure", hop=hop)
        finally:
            _close_quietly(response.close)
    _raise_denied("max_redirects_exceeded", hop=policy.max_redirects + 1)


def _close_quietly(close: Callable[[], None]) -> None:
    try:
        close()
    except Exception:  # noqa: BLE001 - cleanup must not mask the policy outcome
        return


def default_resolve(host: str) -> tuple[str, ...]:
    """Resolve every stream address and return normalized unique IP literals."""
    infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    addresses: list[str] = []
    for info in infos:
        normalized = _normalize_address(str(info[4][0]))
        if normalized and normalized not in addresses:
            addresses.append(normalized)
    return tuple(addresses)


def _is_blocked_address(addr: str) -> bool:
    try:
        ip = ipaddress.ip_address(addr)
    except ValueError:
        return True
    mapped = getattr(ip, "ipv4_mapped", None)
    if mapped is not None:
        return _is_blocked_address(str(mapped))
    return bool(
        not ip.is_global
        or ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


def _looks_private_host(host: str) -> bool:
    normalized = _normalize_host(host)
    if normalized == "localhost" or normalized.endswith(".local"):
        return True
    try:
        packed = socket.inet_aton(normalized)
        normalized = socket.inet_ntoa(packed)
    except OSError:
        pass
    try:
        ipaddress.ip_address(normalized)
    except ValueError:
        return False
    return _is_blocked_address(normalized)


def assert_ssrf_safe(url: str, *, policy: EgressPolicy | None = None) -> str:
    """Compatibility URL validator; network callers must use ``fetch_with_policy``."""
    parsed = _parse_http_url(url)
    if parsed is None:
        raise EgressError("egress denied: invalid_url")
    host = _normalize_host(parsed.hostname or "")
    if not host:
        raise EgressError("egress denied: missing_host")
    if _looks_private_host(host):
        raise EgressError("egress denied: private_address_denied")
    active = policy or EgressPolicy(
        allowed_schemes=frozenset({"http", "https"}),
        allowed_hosts=frozenset({host}),
        allowed_ports=frozenset({80, 443}),
        allow_private_addresses=False,
        deny_by_default=True,
    )
    return active.require(url).url


def decide_redirect_chain(
    start_url: str,
    redirects: list[str],
    *,
    policy: EgressPolicy,
    resolver: Callable[[str], tuple[str, ...]] | None = None,
) -> list[EgressDecision]:
    """Compatibility simulator that re-evaluates every redirect hop."""
    current = start_url
    decisions: list[EgressDecision] = []
    for hop, location in enumerate(("", *redirects)):
        if hop:
            current = urljoin(current, location)
        decisions.append(policy.require(current, hop=hop, resolver=resolver))
    return decisions


def policy_from_allowlist(
    hosts: Mapping[str, object] | Iterable[str],
    **kwargs: object,
) -> EgressPolicy:
    if isinstance(hosts, Mapping):
        allowed = frozenset(_normalize_host(str(key)) for key in hosts)
    else:
        allowed = frozenset(_normalize_host(str(item)) for item in hosts)
    base: dict[str, object] = {
        "allowed_hosts": allowed,
        "allowed_schemes": frozenset({"https", "http"}),
        "deny_by_default": True,
    }
    base.update(kwargs)
    return EgressPolicy(**base)  # type: ignore[arg-type]


def policy_from_security_policy(policy: SecurityEgressPolicy) -> EgressPolicy:
    """Build an ``EgressPolicy`` from ``SecurityPolicy`` composition knobs."""
    return EgressPolicy(
        allowed_hosts=frozenset(_normalize_host(str(item)) for item in policy.egress_allow_hosts),
        allowed_schemes=frozenset({"https", "http"}),
        deny_by_default=policy.egress_deny_by_default,
        allow_private_addresses=False,
    )
