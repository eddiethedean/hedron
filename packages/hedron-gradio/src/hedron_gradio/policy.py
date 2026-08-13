"""Remote destination policy and SSRF defenses for Gradio client interop."""

from __future__ import annotations

import ipaddress
import re
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


def _host_is_private(host: str) -> bool:
    host = normalize_host(host)
    if host in {"localhost", "localhost.localdomain"}:
        return True
    if host.endswith(".localhost"):
        return True
    try:
        addr = ipaddress.ip_address(host)
    except ValueError:
        return False
    return any(addr in net for net in _PRIVATE_NETWORKS)


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
    if not config.allow_private_hosts and _host_is_private(normalized):
        raise GradioRemoteError(f"Private or loopback host blocked for {label}: {normalized!r}")


def redact_sensitive_text(text: str) -> str:
    return _TOKEN_LIKE.sub("***", text)
