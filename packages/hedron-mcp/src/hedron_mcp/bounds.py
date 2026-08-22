"""Request bounds, cancellation, and multi-worker lifecycle (BOUNDS-032)."""

from __future__ import annotations

import threading
import time
import uuid
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any


class BoundsError(PermissionError):
    """Raised when an MCP request exceeds configured Supported bounds."""


@dataclass
class McpBounds:
    """Fail-closed limits for Supported MCP paths.

    Process-local maps are capped and TTL-evicted so long-lived workers cannot
    retain unbounded cancel ids, sessions, or rate keys (#172). These structures
    do not coordinate across workers; multi-worker deployments need an external
    store keyed by ``shared_prefix`` (see ``assert_worker_safe``).
    """

    max_request_bytes: int = 64_000
    max_concurrency: int = 8
    rate_limit_per_minute: int = 120
    default_deadline_seconds: float = 30.0
    shared_prefix: str = "hedron-mcp"
    cancel_ttl_seconds: float = 60.0
    max_cancelled: int = 1_024
    session_ttl_seconds: float = 3_600.0
    max_sessions: int = 256
    rate_window_seconds: float = 60.0
    max_rate_principals: int = 1_024
    _inflight: int = field(default=0, init=False, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)
    _rate_buckets: OrderedDict[str, list[float]] = field(
        default_factory=OrderedDict, init=False, repr=False
    )
    _cancelled: OrderedDict[str, float] = field(default_factory=OrderedDict, init=False, repr=False)
    _sessions: OrderedDict[str, dict[str, Any]] = field(
        default_factory=OrderedDict, init=False, repr=False
    )

    def __post_init__(self) -> None:
        if self.max_rate_principals < 1:
            raise ValueError("max_rate_principals must be >= 1")

    def new_request_id(self) -> str:
        return f"{self.shared_prefix}:{uuid.uuid4().hex}"

    def check_size(self, raw: bytes | str) -> None:
        size = len(raw.encode("utf-8") if isinstance(raw, str) else raw)
        if size > self.max_request_bytes:
            raise BoundsError(f"MCP request exceeds max_request_bytes={self.max_request_bytes}")

    def check_rate(self, principal: str) -> None:
        now = time.monotonic()
        with self._lock:
            self._prune_rate_buckets(now)
            bucket = self._rate_buckets.get(principal)
            if bucket is None:
                while len(self._rate_buckets) >= self.max_rate_principals:
                    self._rate_buckets.popitem(last=False)
                bucket = []
                self._rate_buckets[principal] = bucket
            else:
                self._rate_buckets.move_to_end(principal)
            cutoff = now - self.rate_window_seconds
            pruned = [t for t in bucket if t >= cutoff]
            if len(pruned) >= self.rate_limit_per_minute:
                self._rate_buckets[principal] = pruned
                raise BoundsError("MCP rate limit exceeded")
            pruned.append(now)
            self._rate_buckets[principal] = pruned

    def acquire(self) -> None:
        with self._lock:
            if self._inflight >= self.max_concurrency:
                raise BoundsError("MCP concurrency limit exceeded")
            self._inflight += 1

    def release(self) -> None:
        with self._lock:
            self._inflight = max(0, self._inflight - 1)

    @staticmethod
    def scoped_cancel_key(request_id: str, *, owner: str) -> str:
        """Bind a cancel id to a session or principal so ids cannot cross tenants (#217)."""
        return f"{owner}\x1f{request_id}"

    def request_cancel(self, request_id: str, *, owner: str) -> None:
        key = self.scoped_cancel_key(request_id, owner=owner)
        now = time.monotonic()
        with self._lock:
            self._prune_cancelled(now)
            self._cancelled[key] = now
            self._cancelled.move_to_end(key)
            while len(self._cancelled) > self.max_cancelled:
                self._cancelled.popitem(last=False)

    def is_cancelled(self, request_id: str, *, owner: str) -> bool:
        key = self.scoped_cancel_key(request_id, owner=owner)
        now = time.monotonic()
        with self._lock:
            stamped = self._cancelled.get(key)
            if stamped is None:
                return False
            if now - stamped > self.cancel_ttl_seconds:
                del self._cancelled[key]
                return False
            return True

    def clear_cancel(self, request_id: str, *, owner: str) -> None:
        """Drop a cancel mark once the matching request has finished."""
        key = self.scoped_cancel_key(request_id, owner=owner)
        with self._lock:
            self._cancelled.pop(key, None)

    def open_session(self, session_id: str, *, principal: str, origin: str | None) -> None:
        now = time.monotonic()
        with self._lock:
            self._prune_sessions(now)
            self._sessions[session_id] = {
                "principal": principal,
                "origin": origin,
                "opened_at": time.time(),
                "last_seen": now,
            }
            self._sessions.move_to_end(session_id)
            while len(self._sessions) > self.max_sessions:
                self._sessions.popitem(last=False)

    def close_session(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)

    def session(self, session_id: str) -> dict[str, Any] | None:
        now = time.monotonic()
        with self._lock:
            self._prune_sessions(now)
            data = self._sessions.get(session_id)
            if data is None:
                return None
            data["last_seen"] = now
            self._sessions.move_to_end(session_id)
            return {
                "principal": data.get("principal"),
                "origin": data.get("origin"),
                "opened_at": data.get("opened_at"),
            }

    def assert_worker_safe(self) -> None:
        """Document multi-worker contract: authority must use shared_prefix stores."""
        if not self.shared_prefix:
            raise BoundsError("MCP multi-worker lifecycle requires a non-empty shared_prefix")

    def _prune_cancelled(self, now: float) -> None:
        expired = [
            key
            for key, stamped in self._cancelled.items()
            if now - stamped > self.cancel_ttl_seconds
        ]
        for key in expired:
            del self._cancelled[key]

    def _prune_sessions(self, now: float) -> None:
        expired = [
            key
            for key, data in self._sessions.items()
            if now - float(data.get("last_seen") or 0.0) > self.session_ttl_seconds
        ]
        for key in expired:
            del self._sessions[key]

    def _prune_rate_buckets(self, now: float) -> None:
        cutoff = now - self.rate_window_seconds
        empty: list[str] = []
        for key, bucket in self._rate_buckets.items():
            pruned = [t for t in bucket if t >= cutoff]
            if pruned:
                self._rate_buckets[key] = pruned
            else:
                empty.append(key)
        for key in empty:
            del self._rate_buckets[key]
