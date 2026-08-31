"""Remote destination policy and SSRF defenses for Gradio client interop."""

from __future__ import annotations

import ipaddress
import math
import re
import socket
from dataclasses import dataclass, field
from typing import Any, cast
from urllib.parse import urlparse

from hedron_core.egress import EgressError, EgressPolicy
from hedron_gradio.errors import GradioRemoteError

__all__ = [
    "GradioRemoteConfig",
    "normalize_host",
    "validate_remote_url",
]

_PRIVATE_NETWORKS = (
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
)

_TOKEN_LIKE = re.compile(
    r"(?i)(authorization\s*:|bearer\s+\S+|hf_token\s*=\S+|hf_[a-z0-9]+|api[_-]?key\s*[:=]\S*)"
)


def _default_allowed_hosts() -> frozenset[str]:
    return frozenset()


def normalize_host(host: str) -> str:
    return host.strip().lower().rstrip(".")


def _embedded_ipv4(
    addr: ipaddress.IPv4Address | ipaddress.IPv6Address,
) -> ipaddress.IPv4Address | None:
    """Return the IPv4 address embedded in an IPv4-mapped or IPv4-compatible IPv6 literal."""
    if isinstance(addr, ipaddress.IPv4Address):
        return addr
    mapped = addr.ipv4_mapped
    if mapped is not None:
        return mapped
    packed = addr.packed
    if packed[:12] == bytes(12):
        return ipaddress.IPv4Address(packed[12:])
    return None


def _addr_is_private(addr: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return any(addr in net for net in _PRIVATE_NETWORKS)


def _host_is_private(host: str) -> bool:
    """Return whether a host literal denotes a private or special address."""
    host = normalize_host(host)
    if host in {"localhost", "localhost.localdomain"}:
        return True
    if host.endswith(".localhost"):
        return True
    # Expand abbreviated IPv4 forms accepted by many stacks (e.g. 127.1 → 127.0.0.1).
    try:
        packed = socket.inet_aton(host)
        host = socket.inet_ntoa(packed)
    except OSError:
        pass
    try:
        addr = ipaddress.ip_address(host)
    except ValueError:
        return False
    if _addr_is_private(addr):
        return True
    embedded = _embedded_ipv4(addr)
    return embedded is not None and _addr_is_private(embedded)


@dataclass(frozen=True)
class GradioRemoteConfig:
    """Frozen remote policy for a declared Gradio destination."""

    base_url: str
    allowed_hosts: frozenset[str] = field(default_factory=_default_allowed_hosts)
    allowed_schemes: frozenset[str] = frozenset({"https"})
    allow_private_hosts: bool = False
    max_redirect_hops: int = 0
    tls_verify: bool = True
    request_timeout_seconds: float = 30.0
    max_upload_bytes: int = 8 * 1024 * 1024
    max_download_bytes: int = 32 * 1024 * 1024
    artifact_retention_seconds: float = 300.0

    def __post_init__(self) -> None:
        raw_redirects = cast(Any, self.max_redirect_hops)
        if (
            isinstance(raw_redirects, bool)
            or not isinstance(raw_redirects, int)
            or raw_redirects < 0
        ):
            raise ValueError("max_redirect_hops must be >= 0")
        raw_timeout = cast(Any, self.request_timeout_seconds)
        if (
            isinstance(raw_timeout, bool)
            or not isinstance(raw_timeout, (int, float))
            or not math.isfinite(float(raw_timeout))
            or raw_timeout <= 0
        ):
            raise ValueError("request_timeout_seconds must be > 0")
        for name in ("max_upload_bytes", "max_download_bytes"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        raw_retention = cast(Any, self.artifact_retention_seconds)
        if (
            isinstance(raw_retention, bool)
            or not isinstance(raw_retention, (int, float))
            or not math.isfinite(float(raw_retention))
            or raw_retention <= 0
        ):
            raise ValueError("artifact_retention_seconds must be > 0")

    @classmethod
    def from_base_url(
        cls,
        base_url: str,
        *,
        extra_hosts: frozenset[str] | None = None,
        allow_private_hosts: bool = False,
    ) -> GradioRemoteConfig:
        parsed = urlparse(base_url.strip())
        if not parsed.scheme or not parsed.netloc:
            raise GradioRemoteError(f"Invalid base_url: {base_url!r}")
        host = normalize_host(parsed.hostname or "")
        hosts = {host}
        if extra_hosts:
            hosts.update(normalize_host(item) for item in extra_hosts)
        scheme = parsed.scheme.lower()
        is_private = _host_is_private(host)
        allow_private = allow_private_hosts or is_private
        allowed_schemes: frozenset[str] = frozenset({"https"})
        if scheme == "http" and allow_private:
            allowed_schemes = frozenset({"http", "https"})
        return cls(
            base_url=base_url.strip(),
            allowed_hosts=frozenset(hosts),
            allowed_schemes=allowed_schemes,
            allow_private_hosts=allow_private,
        )


def validate_remote_url(
    url: str,
    config: GradioRemoteConfig,
    *,
    label: str = "destination",
) -> None:
    """Reject disallowed scheme/host and private destinations unless opted in.

    DNS names are resolved (A/AAAA) when ``allow_private_hosts`` is false so
    an allowlisted name cannot point at loopback/link-local/metadata (#268).
    """
    parsed = urlparse(url.strip())
    ports = {80, 443}
    try:
        if parsed.port is not None:
            ports.add(parsed.port)
    except ValueError:
        pass
    shared = EgressPolicy(
        allowed_schemes=config.allowed_schemes,
        allowed_hosts=config.allowed_hosts,
        allowed_ports=frozenset(ports),
        allow_private_addresses=config.allow_private_hosts,
        max_redirects=config.max_redirect_hops,
        connect_deadline_seconds=config.request_timeout_seconds,
        read_deadline_seconds=config.request_timeout_seconds,
        total_deadline_seconds=config.request_timeout_seconds,
        response_budget_bytes=config.max_download_bytes,
        decompressed_budget_bytes=config.max_download_bytes,
    )
    try:
        shared.require(url.strip(), resolver=_resolved_addresses_for_validation)
    except EgressError as exc:
        reason = str(exc).rsplit(": ", 1)[-1]
        if reason == "scheme_denied" or (
            reason == "invalid_url" and parsed.scheme.lower() not in config.allowed_schemes
        ):
            raise GradioRemoteError(
                f"Disallowed {label} scheme; allowed: {sorted(config.allowed_schemes)}"
            ) from exc
        if reason == "host_denied":
            raise GradioRemoteError(f"Host is not in the allowlist for {label}") from exc
        if reason == "private_address_denied":
            raise GradioRemoteError(f"Private or loopback host blocked for {label}") from exc
        raise GradioRemoteError(f"Shared egress policy rejected {label}: {reason}") from exc


def _resolved_addresses_for_validation(host: str) -> tuple[str, ...]:
    """Resolve for preflight; actual I/O must re-resolve through fetch_with_policy."""
    try:
        records = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except OSError:
        # Configuration preflight remains usable offline. This sentinel is not
        # used for a network connection; the shared fetch path resolves again.
        return ("8.8.8.8",)
    return tuple(str(record[4][0]).split("%", 1)[0] for record in records if record[4])


def redact_sensitive_text(text: str) -> str:
    return _TOKEN_LIKE.sub("***", text)
