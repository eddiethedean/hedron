"""Idle and absolute session-timeout helpers for host session dicts.

Stamp ``created`` / ``last_seen`` (or Hedron-prefixed keys) on the application
session mapping, then reject expired sessions. Signed cookies alone cannot
revoke a session early: once issued, a cookie remains valid until its own
expiry or signature failure. Server-side session stores (or rotating refresh
tokens) are required for immediate logout/revocation across devices.
"""

from __future__ import annotations

import time
from collections.abc import MutableMapping
from typing import Any, Literal

__all__ = [
    "SESSION_CREATED_KEY",
    "SESSION_LAST_SEEN_KEY",
    "SessionTimeoutError",
    "check_session_timeout",
    "clear_session_timeout_stamps",
    "stamp_session_created",
    "stamp_session_last_seen",
    "touch_session",
]

SESSION_CREATED_KEY = "hedron_session_created"
SESSION_LAST_SEEN_KEY = "hedron_session_last_seen"


class SessionTimeoutError(Exception):
    """Raised when idle or absolute session limits are exceeded."""

    def __init__(self, reason: Literal["idle", "absolute"], *, message: str | None = None) -> None:
        self.reason = reason
        super().__init__(message or f"session expired ({reason})")


def stamp_session_created(
    session: MutableMapping[str, Any],
    *,
    now: float | None = None,
    key: str = SESSION_CREATED_KEY,
) -> float:
    """Record absolute-session start time; does not overwrite an existing stamp."""
    existing = session.get(key)
    if isinstance(existing, (int, float)):
        return float(existing)
    ts = float(time.time() if now is None else now)
    session[key] = ts
    return ts


def stamp_session_last_seen(
    session: MutableMapping[str, Any],
    *,
    now: float | None = None,
    key: str = SESSION_LAST_SEEN_KEY,
) -> float:
    ts = float(time.time() if now is None else now)
    session[key] = ts
    return ts


def touch_session(
    session: MutableMapping[str, Any],
    *,
    now: float | None = None,
) -> None:
    """Ensure ``created`` exists and refresh ``last_seen``."""
    ts = float(time.time() if now is None else now)
    stamp_session_created(session, now=ts)
    stamp_session_last_seen(session, now=ts)


def clear_session_timeout_stamps(session: MutableMapping[str, Any]) -> None:
    session.pop(SESSION_CREATED_KEY, None)
    session.pop(SESSION_LAST_SEEN_KEY, None)


def check_session_timeout(
    session: MutableMapping[str, Any],
    *,
    idle_seconds: float | None,
    absolute_seconds: float | None,
    now: float | None = None,
    raise_on_expired: bool = True,
    touch: bool = False,
) -> bool:
    """Return True if the session is within limits.

    When expired: raise ``SessionTimeoutError`` if ``raise_on_expired``, else
    return False. Pass ``None`` for a limit to disable that axis.
    Negative limits are rejected (``ValueError``) so misconfiguration cannot
    instantly expire every active session.

    Note: signed cookies alone cannot revoke early — clearing server session
    state (or rotating refresh) is required for immediate invalidation.
    """
    if idle_seconds is not None and float(idle_seconds) < 0:
        raise ValueError(f"idle_seconds must be >= 0 or None, got {idle_seconds!r}")
    if absolute_seconds is not None and float(absolute_seconds) < 0:
        raise ValueError(f"absolute_seconds must be >= 0 or None, got {absolute_seconds!r}")

    ts = float(time.time() if now is None else now)
    created = session.get(SESSION_CREATED_KEY)
    last_seen = session.get(SESSION_LAST_SEEN_KEY)

    if absolute_seconds is not None:
        if not isinstance(created, (int, float)):
            if raise_on_expired:
                raise SessionTimeoutError("absolute", message="session missing created stamp")
            return False
        if ts - float(created) > float(absolute_seconds):
            if raise_on_expired:
                raise SessionTimeoutError("absolute")
            return False

    if idle_seconds is not None:
        if not isinstance(last_seen, (int, float)):
            if raise_on_expired:
                raise SessionTimeoutError("idle", message="session missing last_seen stamp")
            return False
        if ts - float(last_seen) > float(idle_seconds):
            if raise_on_expired:
                raise SessionTimeoutError("idle")
            return False

    if touch:
        touch_session(session, now=ts)
    return True
