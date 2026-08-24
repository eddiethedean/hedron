"""Mount, redirect, and public URL helpers for proxied Hedron apps."""

from __future__ import annotations

import ipaddress
import os
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote, urlencode, urlsplit

from starlette.requests import Request
from starlette.responses import Response

from hedron.mount import normalize_mount_path, prefix_local_path
from hedron.security.redirects import redirect_local
from hedron_core.htmx_contract import is_local_path

_CONNECT_BASE_HEADER = "rstudio-connect-app-base-url"
_DEFAULT_CONNECT_PROXY_PEERS = ("127.0.0.1", "::1")
_WORKBENCH_SESSION_MOUNT = re.compile(r"^/s/[^/]+/p/[^/]+(?:/|$)")


@dataclass(frozen=True, slots=True)
class ExternalBase:
    """A validated public origin and application mount."""

    origin: str
    mount: str
    source: str

    @property
    def url(self) -> str:
        return f"{self.origin}{self.mount}"

    @property
    def ephemeral(self) -> bool:
        return is_ephemeral_workbench_mount(self.mount)


def normalize_http_origin(raw: str) -> str:
    """Return a canonical http(s) origin or raise ``ValueError``."""
    text = str(raw).strip()
    if not text or "\\" in text or any(char.isspace() or ord(char) < 32 for char in text):
        raise ValueError("origin contains whitespace, controls, or backslashes")
    try:
        parsed = urlsplit(text)
        port = parsed.port
    except ValueError as exc:
        raise ValueError("origin has an invalid host or port") from exc
    if (
        parsed.scheme.lower() not in {"http", "https"}
        or not parsed.netloc
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("origin must contain only an http(s) scheme and host")
    scheme = parsed.scheme.lower()
    hostname = parsed.hostname.lower()
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        try:
            host = hostname.encode("idna").decode("ascii")
        except UnicodeError as exc:
            raise ValueError("origin contains an invalid internationalized host") from exc
        if (
            not re.fullmatch(r"[a-z0-9.-]+", host)
            or ".." in host
            or any(
                not label or label.startswith("-") or label.endswith("-")
                for label in host.rstrip(".").split(".")
            )
        ):
            raise ValueError("origin contains an invalid DNS host") from None
        host = host.rstrip(".")
    else:
        host = f"[{address.compressed}]" if address.version == 6 else address.compressed
    default_port = 443 if scheme == "https" else 80
    suffix = f":{port}" if port is not None and port != default_port else ""
    return f"{scheme}://{host}{suffix}"


def is_ephemeral_workbench_mount(mount: str) -> bool:
    """Return whether a mount is tied to a disposable Workbench session."""
    return bool(_WORKBENCH_SESSION_MOUNT.match(normalize_mount_path(mount)))


def _validated_external_base(raw: str, *, source: str) -> ExternalBase:
    text = str(raw).strip()
    if not text or "\\" in text or any(char.isspace() or ord(char) < 32 for char in text):
        raise ValueError("public base URL contains whitespace or control characters")
    try:
        parsed = urlsplit(text)
        # Accessing port makes urllib reject malformed and out-of-range values.
        _ = parsed.port
    except ValueError as exc:
        raise ValueError("public base URL has an invalid host or port") from exc
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or not parsed.hostname:
        raise ValueError("public base URL must be an absolute http(s) URL")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("public base URL must not contain credentials")
    if parsed.query or parsed.fragment:
        raise ValueError("public base URL must not contain a query string or fragment")

    mount = normalize_mount_path(parsed.path)
    if parsed.path not in {"", "/"} and not mount:
        raise ValueError("public base URL contains an unsafe mount path")
    return ExternalBase(
        origin=normalize_http_origin(f"{parsed.scheme}://{parsed.netloc}"),
        mount=mount,
        source=source,
    )


def validate_external_base_url(raw: str) -> ExternalBase:
    """Validate an operator-configured public base URL."""
    return _validated_external_base(raw, source="explicit:external_base_url")


def _scope_peer(request: Request) -> str | None:
    return request.client.host if request.client is not None else None


def _trusted_peer(peer: str | None, trusted_peers: Sequence[str]) -> bool:
    if peer is None:
        return False
    allowed = {str(item).strip() for item in trusted_peers if str(item).strip()}
    if peer in allowed:
        return True
    # Normalize equivalent IPv6 spellings without broadening the allowlist.
    try:
        address = ipaddress.ip_address(peer)
        return any(address == ipaddress.ip_address(item) for item in allowed)
    except ValueError:
        return False


def connect_external_base_from_request(
    request: Request,
    *,
    trusted_peers: Sequence[str] = _DEFAULT_CONNECT_PROXY_PEERS,
    environ: Mapping[str, str] | None = None,
) -> ExternalBase | None:
    """Return a validated Posit Connect base, or ``None`` when absent.

    The Connect header is trusted only when it is singular, its path exactly
    matches ASGI ``root_path``, and either Connect's non-customizable runtime
    marker is present or the immediate peer is explicitly allowlisted. A
    present-but-invalid header raises instead of silently changing origins.
    """
    values = request.headers.getlist(_CONNECT_BASE_HEADER)
    if not values:
        return None
    if len(values) != 1:
        raise ValueError("multiple Posit Connect app base headers were rejected")
    peer = _scope_peer(request)
    env = os.environ if environ is None else environ
    connect_runtime = str(env.get("POSIT_PRODUCT") or "").strip().upper() == "CONNECT"
    if not connect_runtime and not _trusted_peer(peer, trusted_peers):
        raise ValueError("Posit Connect app base header lacked trusted runtime evidence")

    base = _validated_external_base(values[0], source="header:rstudio-connect-app-base-url")
    scope_mount = normalize_mount_path(str(request.scope.get("root_path") or ""))
    if not scope_mount or base.mount != scope_mount:
        raise ValueError("Posit Connect app base path does not match ASGI root_path")
    return base


def compose_external_url(
    path: str,
    *,
    base: ExternalBase,
    query: Mapping[str, object] | Sequence[tuple[str, object]] | None = None,
    fragment: str | None = None,
) -> str:
    """Compose a safe absolute URL beneath ``base`` without double-prefixing."""
    value = str(path)
    parsed_path = urlsplit(value)
    if not is_local_path(value) or parsed_path.query or parsed_path.fragment:
        raise ValueError("external URL path must be a local absolute path without query/fragment")
    mounted = prefix_local_path(value, base.mount)
    result = f"{base.origin}{mounted}"
    if query:
        result += "?" + urlencode(query, doseq=True)
    if fragment is not None:
        if any(ord(char) < 32 for char in str(fragment)):
            raise ValueError("external URL fragment contains control characters")
        result += "#" + quote(str(fragment), safe="")
    return result


def compose_local_url(
    path: str,
    *,
    mount: str = "",
    query: Mapping[str, object] | Sequence[tuple[str, object]] | None = None,
    fragment: str | None = None,
) -> str:
    """Mount-prefix a local path and optionally append query/fragment.

    ``path`` must be a local absolute path without an embedded query or fragment;
    pass those via ``query`` / ``fragment`` instead.
    """
    value = str(path)
    parsed_path = urlsplit(value)
    if not is_local_path(value) or parsed_path.query or parsed_path.fragment:
        raise ValueError(
            "local URL path must be a local absolute path without query/fragment; "
            "pass query= and fragment= instead"
        )
    result = prefix_local_path(value, mount)
    if query:
        if isinstance(query, Mapping):
            items: Sequence[tuple[str, object]] = list(query.items())
        else:
            items = list(query)
        for key, raw in items:
            if raw is None:
                raise ValueError(f"local URL query value for {key!r} must not be None")
        result += "?" + urlencode(query, doseq=True)
    if fragment is not None:
        if any(ord(char) < 32 for char in str(fragment)):
            raise ValueError("local URL fragment contains control characters")
        result += "#" + quote(str(fragment), safe="")
    return result


def browser_mount_from_request(request: Request) -> str:
    scope_mount = normalize_mount_path(str(request.scope.get("root_path") or ""))
    state = getattr(getattr(request, "app", None), "state", None)
    env_mount = str(getattr(state, "hedron_mount_path", "") or "")
    configured = bool(getattr(state, "hedron_mount_was_configured", False))
    return env_mount if env_mount or configured else scope_mount


def local_href(
    path: str,
    *,
    mount: str,
    query: Mapping[str, object] | Sequence[tuple[str, object]] | None = None,
    fragment: str | None = None,
) -> str:
    return compose_local_url(path, mount=mount, query=query, fragment=fragment)


def mounted_redirect(
    url: str,
    *,
    mount: str,
    status_code: int = 303,
    policy: Any | None = None,
    query: Mapping[str, object] | Sequence[tuple[str, object]] | None = None,
    fragment: str | None = None,
) -> Response:
    """Workbench-safe local redirect: mount-prefixed Location, never ``../`` depth."""
    target = compose_local_url(url, mount=mount, query=query, fragment=fragment)
    return redirect_local(target, status_code=status_code, policy=policy, mount=None)
