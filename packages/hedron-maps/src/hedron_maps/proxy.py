"""Optional same-origin map proxy with SSRF bounds. Not imported by compile_map."""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

from hedron_core.codes import HED_MAP_POLICY_0001, HED_MAP_POLICY_0002
from hedron_core.diagnostics import error
from hedron_maps.limits import PROXY_MAX_REDIRECTS, PROXY_RESPONSE_BYTES, PROXY_TIMEOUT_MS
from hedron_maps.spec import MapPolicy

__all__ = ["PROXY_MAX_REDIRECTS", "PROXY_RESPONSE_BYTES", "PROXY_TIMEOUT_MS", "assert_ssrf_safe"]


def _block_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return bool(
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def assert_ssrf_safe(url: str, policy: MapPolicy, *, resolve_dns: bool = True) -> str:
    """Validate a proxy candidate. Does not fetch."""
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise error(
            HED_MAP_POLICY_0002,
            title="Proxy URL must be HTTPS",
            explanation=f"Refused {parsed.scheme!r}.",
            remediation="Only https origins may be proxied.",
        )
    if parsed.username or parsed.password or parsed.path.startswith("//"):
        raise error(
            HED_MAP_POLICY_0002,
            title="Proxy URL credentials rejected",
            explanation="Userinfo and protocol-relative forms are invalid.",
            remediation="Strip credentials; keep exact HTTPS origins.",
        )
    origin = f"{parsed.scheme}://{parsed.netloc.split('@')[-1]}"
    if parsed.port:
        host = parsed.hostname or ""
        origin = f"{parsed.scheme}://{host}"
        # keep host:port when non-default
        if parsed.port not in {443, 80}:
            origin = f"{parsed.scheme}://{host}:{parsed.port}"
    if origin not in policy.allowed_origins:
        raise error(
            HED_MAP_POLICY_0001,
            title="Proxy origin is not allowed",
            explanation=f"{origin} is outside MapPolicy.allowed_origins.",
            remediation="Declare the exact origin before enabling the proxy.",
        )
    host = parsed.hostname
    if host is None:
        raise error(
            HED_MAP_POLICY_0002,
            title="Proxy host missing",
            explanation="HTTPS URL did not parse a host.",
            remediation="Use an exact hostname origin.",
        )
    try:
        literal = ipaddress.ip_address(host)
    except ValueError:
        literal = None
    if literal is not None and _block_ip(literal):
        raise error(
            HED_MAP_POLICY_0002,
            title="Proxy target is a blocked address",
            explanation=f"{host} is not a public address.",
            remediation="Do not proxy loopback, link-local, or private ranges.",
        )
    if resolve_dns and literal is None:
        try:
            infos = socket.getaddrinfo(host, parsed.port or 443, type=socket.SOCK_STREAM)
        except OSError as exc:
            raise error(
                HED_MAP_POLICY_0002,
                title="Proxy DNS resolution failed",
                explanation=str(exc),
                remediation="Reject unresolved proxy hostnames.",
            ) from exc
        for info in infos:
            packed = info[4][0]
            ip = ipaddress.ip_address(packed)
            if _block_ip(ip):
                raise error(
                    HED_MAP_POLICY_0002,
                    title="Proxy DNS resolved to a blocked address",
                    explanation=f"{host} resolved to {ip}.",
                    remediation="Revalidate DNS at request time; deny private ranges.",
                )
    return url
