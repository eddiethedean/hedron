"""Mount and public URL helpers for proxied ASGI apps."""

from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlsplit

from hedron_posit._workbench.mount import normalize_mount_path

_WORKBENCH_SESSION_MOUNT = re.compile(r"^/s/[^/]+/p/[^/]+(?:/|$)")


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
