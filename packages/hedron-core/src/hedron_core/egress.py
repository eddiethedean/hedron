"""Deny-by-default outbound egress / SSRF policy (EGRESS-056)."""

from __future__ import annotations

import ipaddress
import math
import socket
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from typing import Protocol
from urllib.parse import urlparse

from hedron_core.compat import StrEnum


class EgressDecisionKind(StrEnum):
    ALLOW = "allow"
    DENY = "deny"


class EgressError(ValueError):
    """Raised when an outbound fetch is denied."""


class SecurityEgressPolicy(Protocol):
    """Security-policy fields needed to derive an egress policy."""

    egress_allow_hosts: frozenset[str]
    egress_deny_by_default: bool


@dataclass(frozen=True, slots=True)
class EgressDecision:
    kind: EgressDecisionKind
    url: str
    reason: str = ""
    resolved_addresses: tuple[str, ...] = ()
    hop: int = 0
    connect_deadline_seconds: float = 0.0
    response_budget_bytes: int = 0


@dataclass(frozen=True, slots=True)
class EgressPolicy:
    """Transport-neutral egress policy. Deny-by-default until allowlists are set."""

    version: int = 1
    allowed_schemes: frozenset[str] = field(default_factory=lambda: frozenset({"https"}))
    allowed_hosts: frozenset[str] = field(default_factory=frozenset[str])
    allowed_ports: frozenset[int] = field(default_factory=lambda: frozenset({443, 80}))
    allow_private_addresses: bool = False
    max_redirects: int = 3
    connect_deadline_seconds: float = 5.0
    response_budget_bytes: int = 1_048_576
    deny_by_default: bool = True

    def __post_init__(self) -> None:
        if (
            isinstance(self.max_redirects, bool)
            or not isinstance(self.max_redirects, int)
            or self.max_redirects < 0
        ):
            raise ValueError("max_redirects must be a non-negative integer")
        if (
            isinstance(self.connect_deadline_seconds, bool)
            or not isinstance(self.connect_deadline_seconds, (int, float))
            or not math.isfinite(float(self.connect_deadline_seconds))
            or self.connect_deadline_seconds <= 0
        ):
            raise ValueError("connect_deadline_seconds must be finite and > 0")
        if (
            isinstance(self.response_budget_bytes, bool)
            or not isinstance(self.response_budget_bytes, int)
            or self.response_budget_bytes < 1
        ):
            raise ValueError("response_budget_bytes must be a positive integer")

    def decide(
        self,
        url: str,
        *,
        hop: int = 0,
        resolver: Callable[[str], tuple[str, ...]] | None = None,
    ) -> EgressDecision:
        if hop > self.max_redirects:
            return EgressDecision(
                kind=EgressDecisionKind.DENY,
                url=url,
                reason="max_redirects_exceeded",
                hop=hop,
            )
        try:
            parsed = urlparse(url)
            # urllib defers malformed-port validation until ``.port`` is read.
            port = parsed.port
        except ValueError:
            return EgressDecision(
                kind=EgressDecisionKind.DENY,
                url=url,
                reason="invalid_url",
                hop=hop,
            )
        scheme = (parsed.scheme or "").lower()
        host = (parsed.hostname or "").lower()
        if scheme not in self.allowed_schemes:
            return EgressDecision(
                kind=EgressDecisionKind.DENY, url=url, reason="scheme_denied", hop=hop
            )
        if self.deny_by_default and host not in self.allowed_hosts:
            return EgressDecision(
                kind=EgressDecisionKind.DENY, url=url, reason="host_denied", hop=hop
            )
        # ``0`` is an explicitly supplied port, not an omitted port.  Using
        # truthiness here would turn ``https://host:0`` into the default 443
        # and allow it when 443 is allowlisted.
        effective_port = port if port is not None else (443 if scheme == "https" else 80)
        if effective_port not in self.allowed_ports:
            return EgressDecision(
                kind=EgressDecisionKind.DENY, url=url, reason="port_denied", hop=hop
            )
        if parsed.username or parsed.password:
            return EgressDecision(
                kind=EgressDecisionKind.DENY, url=url, reason="userinfo_denied", hop=hop
            )
        if not host:
            return EgressDecision(
                kind=EgressDecisionKind.DENY, url=url, reason="missing_host", hop=hop
            )
        try:
            addresses = (resolver or default_resolve)(host)
        except OSError:
            return EgressDecision(
                kind=EgressDecisionKind.DENY,
                url=url,
                reason="dns_resolution_failed",
                hop=hop,
            )
        if not addresses:
            return EgressDecision(
                kind=EgressDecisionKind.DENY,
                url=url,
                reason="dns_unresolved",
                hop=hop,
            )
        for addr in addresses:
            if not self.allow_private_addresses and _is_blocked_address(addr):
                return EgressDecision(
                    kind=EgressDecisionKind.DENY,
                    url=url,
                    reason="private_address_denied",
                    resolved_addresses=addresses,
                    hop=hop,
                )
        return EgressDecision(
            kind=EgressDecisionKind.ALLOW,
            url=url,
            reason="allowed",
            resolved_addresses=addresses,
            hop=hop,
            connect_deadline_seconds=self.connect_deadline_seconds,
            response_budget_bytes=self.response_budget_bytes,
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
            from hedron_core.security_events import SecurityEvent, emit_security_event

            emit_security_event(
                SecurityEvent(
                    code="egress.denied",
                    detail={"reason": decision.reason, "hop": hop},
                )
            )
            raise EgressError(f"egress denied: {decision.reason} for {url!r}")
        return decision


class EgressTransport(Protocol):
    def fetch(self, url: str, *, decision: EgressDecision) -> bytes: ...


def bounded_response(chunks: Iterable[bytes], *, budget_bytes: int) -> bytes:
    """Collect response chunks under a hard byte budget for transport adapters."""
    if isinstance(budget_bytes, bool) or not isinstance(budget_bytes, int) or budget_bytes < 1:
        raise ValueError("budget_bytes must be a positive integer")
    collected = bytearray()
    for chunk in chunks:
        if not isinstance(chunk, (bytes, bytearray, memoryview)):
            raise EgressError("egress response contained a non-byte chunk")
        collected.extend(chunk)
        if len(collected) > budget_bytes:
            raise EgressError("egress response budget exceeded")
    return bytes(collected)


def default_resolve(host: str) -> tuple[str, ...]:
    """Resolve host addresses. Propagates ``OSError`` so callers fail closed."""
    infos = socket.getaddrinfo(host, None)
    addresses: list[str] = []
    for info in infos:
        addr = info[4][0]
        if addr not in addresses:
            addresses.append(str(addr))
    return tuple(addresses)


def _is_blocked_address(addr: str) -> bool:
    try:
        ip = ipaddress.ip_address(addr)
    except ValueError:
        return True
    mapped = getattr(ip, "ipv4_mapped", None)
    if mapped is not None:
        return _is_blocked_address(str(mapped))
    # Align with maps proxy: block anything that is not globally routable (CGNAT, etc.).
    if not ip.is_global:
        return True
    return bool(
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


def _looks_private_host(host: str) -> bool:
    if host in {"localhost"} or host.endswith(".local"):
        return True
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return False
    return _is_blocked_address(host)


def assert_ssrf_safe(url: str, *, policy: EgressPolicy | None = None) -> str:
    """Compatibility helper used by package adapters (public-host SSRF floor)."""
    try:
        parsed = urlparse(url)
        parsed.port  # noqa: B018  # Force deferred malformed-port validation.
    except ValueError as exc:
        raise EgressError(f"egress denied: invalid_url for {url!r}") from exc
    host = (parsed.hostname or "").lower()
    if not host:
        raise EgressError(f"egress denied: missing_host for {url!r}")
    if _looks_private_host(host):
        raise EgressError(f"egress denied: private_address_denied for {url!r}")
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
    """Re-evaluate every redirect hop."""
    decisions = [policy.require(start_url, hop=0, resolver=resolver)]
    for idx, hop_url in enumerate(redirects, start=1):
        decisions.append(policy.require(hop_url, hop=idx, resolver=resolver))
    return decisions


def policy_from_allowlist(
    hosts: Mapping[str, object] | Iterable[str],
    **kwargs: object,
) -> EgressPolicy:
    if isinstance(hosts, Mapping):
        allowed = frozenset(str(key).lower() for key in hosts)
    else:
        allowed = frozenset(str(item).lower() for item in hosts)
    base = {
        "allowed_hosts": allowed,
        "allowed_schemes": frozenset({"https", "http"}),
        "deny_by_default": True,
    }
    base.update(kwargs)  # type: ignore[arg-type]
    return EgressPolicy(**base)  # type: ignore[arg-type]


def policy_from_security_policy(policy: SecurityEgressPolicy) -> EgressPolicy:
    """Build an ``EgressPolicy`` from ``SecurityPolicy`` composition knobs."""
    hosts = policy.egress_allow_hosts
    deny_by_default = policy.egress_deny_by_default
    return EgressPolicy(
        allowed_hosts=frozenset(str(item).lower() for item in hosts),
        allowed_schemes=frozenset({"https", "http"}),
        deny_by_default=deny_by_default,
        allow_private_addresses=False,
    )
