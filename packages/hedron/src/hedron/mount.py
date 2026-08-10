"""Trusted reverse-proxy mount path helpers (MOUNT-020)."""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin, urlsplit, urlunsplit

from hedron_core.mount import cookie_path_for_mount, normalize_mount_path

__all__ = [
    "MountPath",
    "cookie_path_for_mount",
    "normalize_mount_path",
    "prefix_local_path",
    "resolve_mount_path",
    "resolve_mount_path_from_environ",
]


@dataclass(frozen=True, slots=True)
class MountPath:
    """Resolved application mount path used for cookies, redirects, and HTMX URLs."""

    path: str
    source: str

    @property
    def cookie_path(self) -> str:
        return cookie_path_for_mount(self.path)


def prefix_local_path(url: str, mount: str) -> str:
    """Prefix a local absolute path with ``mount`` once (no double-prefix)."""
    normalized = normalize_mount_path(mount)
    if not normalized:
        return url
    if not url.startswith("/") or url.startswith("//"):
        return url
    # Defense in depth if a caller bypassed normalize_mount_path.
    if normalized.startswith("//") or "://" in normalized:
        return url
    if url == normalized or url.startswith(normalized + "/"):
        return url
    if url == "/":
        return normalized + "/"
    return normalized + url


def resolve_mount_path_from_environ(
    *,
    environ: Mapping[str, str] | None = None,
) -> MountPath | None:
    """Read ``HEDRON_ROOT_PATH`` when set."""
    env = environ if environ is not None else os.environ
    raw = env.get("HEDRON_ROOT_PATH")
    if raw is None or not str(raw).strip():
        return None
    return MountPath(path=normalize_mount_path(raw), source="env:HEDRON_ROOT_PATH")


def resolve_mount_path(
    *,
    root_path: str | None = None,
    headers: Mapping[str, str] | None = None,
    peer: str | None = None,
    trusted_peers: Sequence[str] | None = None,
    prefix_headers: Sequence[str] = ("x-forwarded-prefix",),
    environ: Mapping[str, str] | None = None,
    prefer_env: bool = True,
) -> MountPath:
    """Resolve the external mount path.

    Trust order:
    1. ``HEDRON_ROOT_PATH`` when ``prefer_env`` (operator override).
    2. ASGI ``root_path`` when present.
    3. Allowlisted peer + prefix header (ignored when peer is untrusted).
    """
    if prefer_env:
        from_env = resolve_mount_path_from_environ(environ=environ)
        if from_env is not None:
            return from_env

    asgi = normalize_mount_path(root_path)
    if asgi:
        return MountPath(path=asgi, source="asgi:root_path")

    if trusted_peers is not None and peer is not None and headers is not None:
        trusted = {item.strip() for item in trusted_peers if item and item.strip()}
        if peer in trusted:
            lowered = {str(k).lower(): str(v) for k, v in headers.items()}
            for name in prefix_headers:
                raw = lowered.get(name.lower())
                if raw and raw.strip():
                    return MountPath(
                        path=normalize_mount_path(raw),
                        source=f"header:{name.lower()}",
                    )
    # Untrusted forwarded headers are ignored by default.
    return MountPath(path="", source="default")


def external_base_url(
    *,
    scheme: str,
    host: str,
    mount: str,
) -> str:
    """Build ``scheme://host[/mount]`` without a trailing slash (except bare origin)."""
    base = f"{scheme}://{host}"
    normalized = normalize_mount_path(mount)
    return urljoin(base + "/", normalized.lstrip("/") + "/") if normalized else base


def strip_double_slash_path(url: str) -> str:
    """Collapse accidental ``//`` in the path component of a local URL."""
    parts = urlsplit(url)
    if parts.scheme or parts.netloc:
        path = parts.path.replace("//", "/")
        return urlunsplit((parts.scheme, parts.netloc, path, parts.query, parts.fragment))
    return url.replace("//", "/") if url.startswith("/") else url


def mount_from_request(request: Any, *, trusted_peers: Sequence[str] | None = None) -> MountPath:
    """Resolve mount path from a Starlette/FastAPI request."""
    scope = getattr(request, "scope", {}) or {}
    headers = {
        k.decode() if isinstance(k, bytes) else str(k): (
            v.decode() if isinstance(v, bytes) else str(v)
        )
        for k, v in (scope.get("headers") or [])
    }
    client = scope.get("client")
    peer = client[0] if isinstance(client, (list, tuple)) and client else None
    return resolve_mount_path(
        root_path=str(scope.get("root_path") or "") or None,
        headers=headers,
        peer=peer,
        trusted_peers=trusted_peers,
    )
