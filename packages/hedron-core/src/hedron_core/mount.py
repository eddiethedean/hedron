"""Shared mount-path helpers for cookie Path and local URL prefixing."""

from __future__ import annotations

__all__ = [
    "cookie_path_for_mount",
    "normalize_mount_path",
]


def normalize_mount_path(value: str | None) -> str:
    """Normalize a mount path to ``''`` (site root) or ``/prefix`` (no trailing slash).

    Protocol-relative (``//host``) and absolute URL mounts are rejected as empty so
    they cannot become scheme-relative open redirects via path prefixing.
    """
    if value is None:
        return ""
    text = str(value).strip()
    if not text or text == "/":
        return ""
    # Fail closed: never accept scheme-relative or absolute URL mounts.
    if text.startswith("//") or "://" in text or "\\" in text or any(ch.isspace() for ch in text):
        return ""
    if not text.startswith("/"):
        text = "/" + text
    normalized = text.rstrip("/") or ""
    if "//" in normalized:
        return ""
    return normalized


def cookie_path_for_mount(mount: str) -> str:
    """Return a cookie ``Path`` for the mount (``/`` at site root).

    Uses the normalized mount without a forced trailing slash so Path ``/app``
    matches both ``/app`` and ``/app/...`` (RFC 6265 path-matches).
    """
    normalized = normalize_mount_path(mount)
    return normalized if normalized else "/"
