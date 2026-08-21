"""Deny-by-default outbound egress / SSRF policy (EGRESS-056)."""

from __future__ import annotations

import ipaddress
import socket
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol
from urllib.parse import urlparse


class EgressDecisionKind(StrEnum):
    ALLOW = "allow"
    DENY = "deny"


class EgressError(ValueError):
    """Raised when an outbound fetch is denied."""


@dataclass(frozen=True, slots=True)
class EgressDecision:
    kind: EgressDecisionKind
    url: str
    reason: str = ""
    resolved_addresses: tuple[str, ...] = ()
    hop: int = 0


@dataclass(frozen=True, slots=True)
class EgressPolicy:
    """Transport-neutral egress policy. Deny-by-default until allowlists are set."""

    version: int = 1
    allowed_schemes: frozenset[str] = field(default_factory=lambda: frozenset({"https"}))
    allowed_hosts: frozenset[str] = field(default_factory=frozenset)
    allowed_ports: frozenset[int] = field(default_factory=lambda: frozenset({443, 80}))
    allow_private_addresses: bool = False
    max_redirects: int = 3
    connect_deadline_seconds: float = 5.0
    response_budget_bytes: int = 1_048_576
    deny_by_default: bool = True

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
        parsed = urlparse(url)
        scheme = (parsed.scheme or "").lower()
        host = (parsed.hostname or "").lower()
        port = parsed.port
        if scheme not in self.allowed_schemes:
            return EgressDecision(
                kind=EgressDecisionKind.DENY, url=url, reason="scheme_denied", hop=hop
            )
        if self.deny_by_default and host not in self.allowed_hosts:
            return EgressDecision(
                kind=EgressDecisionKind.DENY, url=url, reason="host_denied", hop=hop
            )
        effective_port = port or (443 if scheme == "https" else 80)
        if effective_port not in self.allowed_ports:
            return EgressDecision(
                kind=EgressDecisionKind.DENY, url=url, reason="port_denied", hop=hop
            )
        if parsed.username or parsed.password:
            return EgressDecision(
                kind=EgressDecisionKind.DENY, url=url, reason="userinfo_denied", hop=hop
            )
        addresses = (resolver or default_resolve)(host) if host else ()
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
            raise EgressError(f"egress denied: {decision.reason} for {url!r}")
        return decision


class EgressTransport(Protocol):
    def fetch(self, url: str, *, decision: EgressDecision) -> bytes: ...


def default_resolve(host: str) -> tuple[str, ...]:
    try:
        infos = socket.getaddrinfo(host, None)
    except OSError:
        return ()
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
        return _is_blocked_address(host)
    except ValueError:
        return False


def assert_ssrf_safe(url: str, *, policy: EgressPolicy | None = None) -> str:
    """Compatibility helper used by package adapters (public-host SSRF floor)."""
    parsed = urlparse(url)
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
) -> list[EgressDecision]:
    """Re-evaluate every redirect hop."""
    decisions = [policy.require(start_url, hop=0)]
    for idx, hop_url in enumerate(redirects, start=1):
        decisions.append(policy.require(hop_url, hop=idx))
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
