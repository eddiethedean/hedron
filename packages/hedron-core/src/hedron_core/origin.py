"""Same-origin helpers shared by WebSocket and navigation preload."""

from __future__ import annotations

from urllib.parse import urlparse

__all__ = ["effective_port", "is_same_origin"]


def effective_port(scheme: str, port: int | None) -> int:
    if port is not None:
        return port
    return 443 if scheme in {"https", "wss"} else 80


def is_same_origin(
    origin: str,
    *,
    request_scheme: str,
    request_hostname: str | None,
    request_port: int | None,
) -> bool:
    """Compare Origin to a request URL using scheme + host + effective port.

    Browser WebSocket upgrades use ``ws``/``wss`` while Origin uses ``http``/``https``.
    """
    try:
        parsed = urlparse(origin)
        port = parsed.port
    except ValueError:
        return False
    if not parsed.hostname or not parsed.scheme or not request_hostname:
        return False
    origin_scheme = parsed.scheme.lower()
    req_scheme = (request_scheme or "http").lower()
    if origin_scheme in {"http", "https"} and req_scheme in {"ws", "wss"}:
        req_http = "https" if req_scheme == "wss" else "http"
    else:
        req_http = req_scheme
    if origin_scheme != req_http:
        return False
    if parsed.hostname != request_hostname:
        return False
    return effective_port(origin_scheme, port) == effective_port(req_http, request_port)
