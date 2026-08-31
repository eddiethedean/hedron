"""Idle and absolute session-timeout helpers for host session dicts.

Stamp ``created`` / ``last_seen`` (or Hedron-prefixed keys) on the application
session mapping, then reject expired sessions. Signed cookies alone cannot
revoke a session early: once issued, a cookie remains valid until its own
expiry or signature failure. Server-side session stores (or rotating refresh
tokens) are required for immediate logout/revocation across devices.
"""

from __future__ import annotations

import math
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


def _finite_float(value: object, *, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number, got {value!r}")
    try:
        numeric = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} must be a finite number, got {value!r}") from exc
    if not math.isfinite(numeric):
        raise ValueError(f"{name} must be a finite number, got {value!r}")
    return numeric


def stamp_session_created(
    session: MutableMapping[str, Any],
    *,
    now: float | None = None,
    key: str = SESSION_CREATED_KEY,
) -> float:
    """Record absolute-session start time; does not overwrite an existing stamp."""
    existing = session.get(key)
    if isinstance(existing, (int, float)) and not isinstance(existing, bool):
        try:
            existing_float = float(existing)
        except OverflowError:
            existing_float = math.inf
        if math.isfinite(existing_float):
            return existing_float
    ts = _finite_float(time.time() if now is None else now, name="now")
    session[key] = ts
    return ts


def stamp_session_last_seen(
    session: MutableMapping[str, Any],
    *,
    now: float | None = None,
    key: str = SESSION_LAST_SEEN_KEY,
) -> float:
    ts = _finite_float(time.time() if now is None else now, name="now")
    session[key] = ts
    return ts


def touch_session(
    session: MutableMapping[str, Any],
    *,
    now: float | None = None,
) -> None:
    """Ensure ``created`` exists and refresh ``last_seen``."""
    ts = _finite_float(time.time() if now is None else now, name="now")
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
    for name, value in (("idle_seconds", idle_seconds), ("absolute_seconds", absolute_seconds)):
        if value is not None:
            try:
                numeric = _finite_float(value, name=name)
            except ValueError:
                raise ValueError(f"{name} must be finite and >= 0 or None, got {value!r}") from None
            if numeric < 0:
                raise ValueError(f"{name} must be finite and >= 0 or None, got {value!r}")

    ts = _finite_float(time.time() if now is None else now, name="now")
    created = session.get(SESSION_CREATED_KEY)
    last_seen = session.get(SESSION_LAST_SEEN_KEY)

    if absolute_seconds is not None:
        if not isinstance(created, (int, float)) or isinstance(created, bool):
            if raise_on_expired:
                raise SessionTimeoutError("absolute", message="session missing created stamp")
            return False
        try:
            created_ts = float(created)
        except OverflowError:
            created_ts = math.inf
        if not math.isfinite(created_ts) or ts - created_ts > float(absolute_seconds):
            if raise_on_expired:
                raise SessionTimeoutError("absolute")
            return False

    if idle_seconds is not None:
        if not isinstance(last_seen, (int, float)) or isinstance(last_seen, bool):
            if raise_on_expired:
                raise SessionTimeoutError("idle", message="session missing last_seen stamp")
            return False
        try:
            last_seen_ts = float(last_seen)
        except OverflowError:
            last_seen_ts = math.inf
        if not math.isfinite(last_seen_ts) or ts - last_seen_ts > float(idle_seconds):
            if raise_on_expired:
                raise SessionTimeoutError("idle")
            return False

    if touch:
        touch_session(session, now=ts)
    return True
