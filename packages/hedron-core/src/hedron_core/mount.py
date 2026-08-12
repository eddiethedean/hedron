"""Shared mount-path helpers for cookie Path and local URL prefixing."""

from __future__ import annotations

from urllib.parse import unquote

__all__ = [
    "cookie_path_for_mount",
    "normalize_mount_path",
    "prefix_local_path",
]

_DECODE_ROUNDS = 3


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
    # Fail closed: never accept scheme-relative or absolute URL mounts.
    if (
        text.startswith("//")
        or "://" in text
        or "\\" in text
        or "?" in text
        or "#" in text
        or any(ch.isspace() for ch in text)
    ):
        return ""
    if not text.startswith("/"):
        text = "/" + text
    normalized = text.rstrip("/") or ""
    if "//" in normalized:
        return ""
    if not normalized:
        return ""
    # Reject traversal / current-dir segments (literal or percent-encoded).
    for segment in normalized.split("/")[1:]:
        if not segment or _segment_is_dot_or_dotdot(segment):
            return ""
    # Defense in depth after decoding the whole path.
    decoded = normalized
    for _ in range(_DECODE_ROUNDS):
        next_decoded = unquote(decoded)
        if next_decoded == decoded:
            break
        decoded = next_decoded
        if "//" in decoded or "\\" in decoded or "://" in decoded:
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


def prefix_local_path(url: str, mount: str) -> str:
    """Prefix a local absolute path with ``mount`` once (no double-prefix)."""
    from hedron_core.htmx_contract import is_local_path

    normalized = normalize_mount_path(mount)
    if not normalized:
        return url
    if not url.startswith("/") or url.startswith("//"):
        return url
    if normalized.startswith("//") or "://" in normalized:
        return url
    suffix_at = min((index for token in "?#" if (index := url.find(token)) >= 0), default=len(url))
    url_path = url[:suffix_at]
    if url_path == normalized or url_path.startswith(normalized + "/"):
        return url
    prefixed = normalized + "/" if url == "/" else normalized + url
    if not is_local_path(prefixed):
        return url
    return prefixed
