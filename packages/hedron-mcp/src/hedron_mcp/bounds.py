"""Request bounds, cancellation, and multi-worker lifecycle (BOUNDS-032)."""

from __future__ import annotations

import threading
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


class BoundsError(PermissionError):
    """Raised when an MCP request exceeds configured Supported bounds."""


@dataclass
class McpBounds:
    """Fail-closed limits for Supported MCP paths."""

    max_request_bytes: int = 64_000
    max_concurrency: int = 8
    rate_limit_per_minute: int = 120
    default_deadline_seconds: float = 30.0
    shared_prefix: str = "hedron-mcp"
    _inflight: int = field(default=0, init=False, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)
    _rate_buckets: dict[str, list[float]] = field(
        default_factory=lambda: defaultdict(list), init=False, repr=False
    )
    _cancelled: set[str] = field(default_factory=set, init=False, repr=False)
    _sessions: dict[str, dict[str, Any]] = field(default_factory=dict, init=False, repr=False)

    def new_request_id(self) -> str:
        return f"{self.shared_prefix}:{uuid.uuid4().hex}"

    def check_size(self, raw: bytes | str) -> None:
        size = len(raw.encode("utf-8") if isinstance(raw, str) else raw)
        if size > self.max_request_bytes:
            raise BoundsError(f"MCP request exceeds max_request_bytes={self.max_request_bytes}")

    def check_rate(self, principal: str) -> None:
        now = time.monotonic()
        with self._lock:
            bucket = self._rate_buckets[principal]
            cutoff = now - 60.0
            self._rate_buckets[principal] = [t for t in bucket if t >= cutoff]
            if len(self._rate_buckets[principal]) >= self.rate_limit_per_minute:
                raise BoundsError("MCP rate limit exceeded")
            self._rate_buckets[principal].append(now)

    def acquire(self) -> None:
        with self._lock:
            if self._inflight >= self.max_concurrency:
                raise BoundsError("MCP concurrency limit exceeded")
            self._inflight += 1

    def release(self) -> None:
        with self._lock:
            self._inflight = max(0, self._inflight - 1)

    def request_cancel(self, request_id: str) -> None:
        with self._lock:
            self._cancelled.add(request_id)

    def is_cancelled(self, request_id: str) -> bool:
        with self._lock:
            return request_id in self._cancelled

    def open_session(self, session_id: str, *, principal: str, origin: str | None) -> None:
        with self._lock:
            self._sessions[session_id] = {
                "principal": principal,
                "origin": origin,
                "opened_at": time.time(),
            }

    def close_session(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)

    def session(self, session_id: str) -> dict[str, Any] | None:
        with self._lock:
            data = self._sessions.get(session_id)
            return dict(data) if data else None

    def assert_worker_safe(self) -> None:
        """Document multi-worker contract: authority must use shared_prefix stores."""
        if not self.shared_prefix:
            raise BoundsError("MCP multi-worker lifecycle requires a non-empty shared_prefix")
