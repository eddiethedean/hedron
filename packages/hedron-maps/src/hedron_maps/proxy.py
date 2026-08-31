"""Optional same-origin map proxy policy backed by shared Hedron egress."""

from __future__ import annotations

import ipaddress
from collections.abc import Callable
from urllib.parse import urlsplit

from hedron_core.codes import HED_MAP_POLICY_0001, HED_MAP_POLICY_0002
from hedron_core.diagnostics import error
from hedron_core.egress import EgressError, EgressPolicy, default_resolve
from hedron_maps.limits import PROXY_MAX_REDIRECTS, PROXY_RESPONSE_BYTES, PROXY_TIMEOUT_MS
from hedron_maps.spec import MapPolicy

__all__ = ["PROXY_MAX_REDIRECTS", "PROXY_RESPONSE_BYTES", "PROXY_TIMEOUT_MS", "assert_ssrf_safe"]


def assert_ssrf_safe(url: str, policy: MapPolicy, *, resolve_dns: bool = True) -> str:
    """Validate a proxy candidate through the shared egress authority.

    This compatibility helper only validates. A proxy implementation that
    performs the request must use ``fetch_with_policy`` so the connection is
    bound to the validated address set.
    """
    if not policy.remote_requests_permitted:
        raise error(
            HED_MAP_POLICY_0001,
            title="Remote map requests are not permitted",
            explanation=(
                "The map proxy cannot fetch remote tiles when remote_requests_permitted is false."
            ),
            remediation="Set remote_requests_permitted=True or serve tiles same-origin.",
        )

    allowed_hosts: set[str] = set()
    allowed_ports: set[int] = {443}
    for origin in policy.allowed_origins:
        try:
            parsed = urlsplit(origin)
            port = parsed.port
        except ValueError:
            continue
        if parsed.hostname:
            allowed_hosts.add(parsed.hostname)
        allowed_ports.add(port if port is not None else 443)

    shared = EgressPolicy(
        allowed_schemes=frozenset({"https"}),
        allowed_hosts=frozenset(allowed_hosts),
        allowed_origins=frozenset(policy.allowed_origins),
        allowed_ports=frozenset(allowed_ports),
        max_redirects=PROXY_MAX_REDIRECTS,
        connect_deadline_seconds=PROXY_TIMEOUT_MS / 1000,
        read_deadline_seconds=PROXY_TIMEOUT_MS / 1000,
        total_deadline_seconds=PROXY_TIMEOUT_MS / 1000,
        response_budget_bytes=PROXY_RESPONSE_BYTES,
    )
    resolver: Callable[[str], tuple[str, ...]] | None = None
    if not resolve_dns:
        resolver = _literal_or_preflight_address
    try:
        return shared.require(url, resolver=resolver).url
    except EgressError as exc:
        reason = str(exc).rsplit(": ", 1)[-1]
        if reason in {"host_denied", "origin_denied"} or (
            reason == "port_denied" and ":0" not in urlsplit(url).netloc
        ):
            raise error(
                HED_MAP_POLICY_0001,
                title="Proxy origin is not allowed",
                explanation="The proxy URL is outside MapPolicy.allowed_origins.",
                remediation="Declare the exact origin before enabling the proxy.",
            ) from exc
        if reason == "port_denied" and ":0" in urlsplit(url).netloc:
            explanation = "Port 0 is not a valid remote HTTPS destination."
        else:
            explanation = f"Shared egress policy rejected the proxy URL ({reason})."
        raise error(
            HED_MAP_POLICY_0002,
            title="Unsafe map proxy URL",
            explanation=explanation,
            remediation="Use an allowlisted public HTTPS origin and a valid port.",
        ) from exc


def _literal_or_preflight_address(host: str) -> tuple[str, ...]:
    """Preserve the historical no-DNS test seam without weakening literals."""
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return ("8.8.8.8",)
    return default_resolve(host)
