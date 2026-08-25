"""Shared mount-path helpers for cookie Path and local URL prefixing."""

from __future__ import annotations

import re
from urllib.parse import unquote, urlparse

__all__ = [
    "cookie_path_for_mount",
    "is_local_path",
    "normalize_mount_path",
    "path_has_mount_prefix",
    "prefix_local_path",
]

_DECODE_ROUNDS = 3
_LOCAL_PATH = re.compile(r"^/[A-Za-z0-9._~!$&'()*+,;=:@%/\-]*$")


def _segment_is_dot_or_dotdot(segment: str) -> bool:
    """True when a path segment is ``.`` / ``..`` (including percent-encoded forms)."""
    if not segment:
        return False
    decoded = segment
    for _ in range(_DECODE_ROUNDS):
        next_decoded = unquote(decoded)
        if next_decoded == decoded:
            break
        decoded = next_decoded
    lowered = decoded.lower()
    return lowered in {".", ".."}


def _path_has_traversal(candidate: str) -> bool:
    lowered = candidate.lower()
    if "%2e%2e" in lowered or "%2e." in lowered or ".%2e" in lowered:
        return True
    normalized = candidate.replace(";", "/")
    parts = [p for p in normalized.split("/") if p not in {"", "."}]
    return any(part == ".." or part.startswith("..") for part in parts)


def is_local_path(url: str) -> bool:
    """Same-origin relative path check used by approved redirect/location headers."""
    if "\\" in url or any(ord(ch) < 32 for ch in url):
        return False
    decoded = url
    for _ in range(_DECODE_ROUNDS):
        next_decoded = unquote(decoded)
        if next_decoded == decoded:
            break
        decoded = next_decoded
        if "\\" in decoded or any(ord(ch) < 32 for ch in decoded):
            return False
        if decoded.startswith("//") or "://" in decoded:
            return False
    parsed = urlparse(url)
    if parsed.scheme or parsed.netloc:
        return False
    if not url.startswith("/") or url.startswith("//"):
        return False
    if decoded.startswith("//"):
        return False
    path = parsed.path or "/"
    decoded_path = urlparse(decoded).path or "/"
    for candidate in (path, decoded_path, url, decoded):
        if _path_has_traversal(candidate):
            return False
    return (
        _LOCAL_PATH.fullmatch(path) is not None and _LOCAL_PATH.fullmatch(decoded_path) is not None
    )


def normalize_mount_path(value: str | None) -> str:
    """Normalize a mount path to ``''`` (site root) or ``/prefix`` (no trailing slash).

    Protocol-relative (``//host``) and absolute URL mounts are rejected as empty so
    they cannot become scheme-relative open redirects via path prefixing.
    Path segments of ``.`` / ``..`` (including percent-encoded ``%2e`` forms) are
    also rejected so cookie Path and redirect prefixes cannot escape the mount.
    """
    if value is None:
        return ""
    text = str(value).strip()
    if not text or text == "/":
        return ""
    if (
        text.startswith("//")
        or "://" in text
        or "\\" in text
        or "?" in text
        or "#" in text
        or any(ch.isspace() for ch in text)
        # Cookie Path is a Set-Cookie attribute value; reject separators/CTL (#245).
        or any(ch in ';,"=' or ord(ch) < 32 for ch in text)
    ):
        return ""
    if not text.startswith("/"):
        text = "/" + text
    normalized = text.rstrip("/") or ""
    if "//" in normalized:
        return ""
    if not normalized:
        return ""
    for segment in normalized.split("/")[1:]:
        if not segment or _segment_is_dot_or_dotdot(segment):
            return ""
    decoded = normalized
    for _ in range(_DECODE_ROUNDS):
        next_decoded = unquote(decoded)
        if next_decoded == decoded:
            break
        decoded = next_decoded
        if "//" in decoded or "\\" in decoded or "://" in decoded:
            return ""
        if any(ch in ';,"=' or ord(ch) < 32 for ch in decoded):
            return ""
        for segment in decoded.split("/")[1:]:
            if not segment or segment in {".", ".."}:
                return ""
    return normalized


def cookie_path_for_mount(mount: str) -> str:
    """Return a cookie ``Path`` for the mount (``/`` at site root).

    Uses the normalized mount without a forced trailing slash so Path ``/app``
    matches both ``/app`` and ``/app/...`` (RFC 6265 path-matches).
    """
    normalized = normalize_mount_path(mount)
    return normalized if normalized else "/"


def path_has_mount_prefix(path: str, mount: str) -> bool:
    """Return True when ``path`` is exactly ``mount`` or a child of ``mount``."""
    normalized = normalize_mount_path(mount)
    if not normalized:
        return False
    suffix_at = min(
        (index for token in "?#" if (index := path.find(token)) >= 0), default=len(path)
    )
    url_path = path[:suffix_at]
    return url_path == normalized or url_path.startswith(normalized + "/")


def prefix_local_path(url: str, mount: str) -> str:
    """Prefix a local absolute path with ``mount`` once (no double-prefix)."""
    normalized = normalize_mount_path(mount)
    if not normalized:
        return url
    if not url.startswith("/") or url.startswith("//"):
        return url
    if normalized.startswith("//") or "://" in normalized:
        return url
    if path_has_mount_prefix(url, normalized):
        return url
    prefixed = normalized + "/" if url == "/" else normalized + url
    if not is_local_path(prefixed):
        return url
    return prefixed
