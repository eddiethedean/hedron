"""Remote destination policy and SSRF defenses for Gradio client interop."""

from __future__ import annotations

import ipaddress
import re
import socket
from dataclasses import dataclass, field
from urllib.parse import urlparse

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
    """True for loopback/private *literals* (not DNS). See ``_first_private_resolved_address``."""
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


def _ip_literal(host: str) -> bool:
    try:
        socket.inet_aton(host)
        return True
    except OSError:
        pass
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def _first_private_resolved_address(host: str) -> str | None:
    """Return the first A/AAAA that is private, or ``None`` if DNS fails or is public.

    Resolution is sampled at validation time. DNS TTL rebinding between this
    check and the HTTP connect remains a residual unless ``allow_private_hosts``.
    """
    host = normalize_host(host)
    if not host or _ip_literal(host):
        return None
    try:
        records = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except OSError:
        return None
    for _family, _type, _proto, _canon, sockaddr in records:
        if not sockaddr:
            continue
        raw = str(sockaddr[0])
        if "%" in raw:
            raw = raw.split("%", 1)[0]
        if _host_is_private(raw):
            return raw
    return None


@dataclass(frozen=True)
class GradioRemoteConfig:
    """Frozen remote policy for a declared Gradio destination."""

    base_url: str
    allowed_hosts: frozenset[str] = field(default_factory=frozenset)
    allowed_schemes: frozenset[str] = frozenset({"https"})
    allow_private_hosts: bool = False
    max_redirect_hops: int = 0
    tls_verify: bool = True
    request_timeout_seconds: float = 30.0
    max_upload_bytes: int = 8 * 1024 * 1024
    max_download_bytes: int = 32 * 1024 * 1024
    artifact_retention_seconds: float = 300.0

    def __post_init__(self) -> None:
        if self.max_redirect_hops < 0:
            raise ValueError("max_redirect_hops must be >= 0")
        if self.request_timeout_seconds <= 0:
            raise ValueError("request_timeout_seconds must be > 0")

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
    scheme = (parsed.scheme or "").lower()
    if scheme not in config.allowed_schemes:
        raise GradioRemoteError(
            f"Disallowed {label} scheme {scheme!r}; allowed: {sorted(config.allowed_schemes)}"
        )
    host = parsed.hostname
    if not host:
        raise GradioRemoteError(f"Missing host in {label} URL: {url!r}")
    normalized = normalize_host(host)
    if normalized not in config.allowed_hosts:
        raise GradioRemoteError(f"Host {normalized!r} is not in the allowlist for {label}")
    if config.allow_private_hosts:
        return
    if _host_is_private(normalized):
        raise GradioRemoteError(f"Private or loopback host blocked for {label}: {normalized!r}")
    resolved_private = _first_private_resolved_address(normalized)
    if resolved_private is not None:
        raise GradioRemoteError(
            f"Private or loopback host blocked for {label}: {normalized!r} "
            f"(resolved {resolved_private})"
        )


def redact_sensitive_text(text: str) -> str:
    return _TOKEN_LIKE.sub("***", text)
