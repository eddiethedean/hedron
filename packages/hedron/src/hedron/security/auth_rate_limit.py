"""In-memory auth-endpoint rate limiting with 429 + Retry-After helpers.

Keyed by IP + route. This process-local sliding window is complementary to
ingress throttling: it does **not** coordinate across multiple workers or
hosts. Prefer edge/WAF limits for production multi-worker deployments; use
this helper for single-process demos and defense-in-depth near login routes.
"""

from __future__ import annotations

import math
import os
import threading
import time
from collections import deque
from collections.abc import Callable, Collection
from heapq import heappop, heappush
from typing import Any, cast

from fastapi import HTTPException, Request, status
from starlette.responses import JSONResponse, Response

__all__ = [
    "AuthRateLimiter",
    "auth_rate_limit_dependency",
    "auth_rate_limit_exception",
    "auth_rate_limit_response",
]


def _trusted_proxy_peers(request: Request) -> set[str]:
    peers: set[str] = set()
    raw_env = os.environ.get("HEDRON_TRUSTED_PROXIES", "")
    peers.update(part.strip() for part in raw_env.split(",") if part.strip())
    app: object | None = request.scope.get("app")
    state = getattr(app, "state", None) if app is not None else None
    configured = getattr(state, "hedron_trusted_peers", None) if state is not None else None
    if isinstance(configured, (list, tuple, set, frozenset)):
        peers.update(
            str(item).strip() for item in cast(Collection[object], configured) if str(item).strip()
        )
    return peers


def _client_ip_for_rate_limit(request: Request) -> str:
    """Return the client IP, honoring ``X-Forwarded-For`` only from trusted peers."""
    direct = request.client.host if request.client else "unknown"
    peers = _trusted_proxy_peers(request)
    if not peers or direct not in peers:
        return direct
    forwarded = request.headers.get("x-forwarded-for", "")
    first = forwarded.split(",")[0].strip() if forwarded else ""
    return first or direct


def auth_rate_limit_exception(
    retry_after: int,
    *,
    detail: str = "Too many authentication attempts",
) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=detail,
        headers={"Retry-After": str(max(1, int(retry_after)))},
    )


def auth_rate_limit_response(
    retry_after: int,
    *,
    detail: str = "Too many authentication attempts",
) -> Response:
    """FastAPI/Starlette 429 response with ``Retry-After``."""
    seconds = max(1, int(retry_after))
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": detail},
        headers={"Retry-After": str(seconds)},
    )


class AuthRateLimiter:
    """Sliding-window limiter: at most ``limit`` events per ``window_seconds`` per key.

    ``max_keys`` bounds process-local state under high-cardinality client input.
    New keys fail closed while the budget is full so active clients cannot reset
    their limits by churning attacker-controlled keys.

    Multi-worker note: each process keeps its own counters. Do not rely on this
    alone for horizontally scaled auth endpoints.
    """

    def __init__(
        self,
        *,
        limit: int = 10,
        window_seconds: float = 60.0,
        max_keys: int = 10_000,
    ) -> None:
        if limit < 1:
            raise ValueError("limit must be >= 1")
        if isinstance(window_seconds, bool) or not math.isfinite(float(window_seconds)):
            raise ValueError("window_seconds must be finite")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be > 0")
        if isinstance(max_keys, bool) or max_keys < 1:
            raise ValueError("max_keys must be >= 1")
        self.limit = int(limit)
        self.window_seconds = float(window_seconds)
        self.max_keys = int(max_keys)
        self._events: dict[str, deque[float]] = {}
        self._expiry: list[tuple[float, str]] = []
        self._lock = threading.Lock()

    def _key(self, ip: str, route: str) -> str:
        return f"{ip}\0{route}"

    def _prune_expired_unlocked(self, cutoff: float) -> None:
        """Drop expired buckets using the next-expiry heap (under lock)."""
        while self._expiry and self._expiry[0][0] <= cutoff + self.window_seconds:
            _expires_at, key = heappop(self._expiry)
            bucket = self._events.get(key)
            if bucket is None:
                continue
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()
            if bucket:
                heappush(self._expiry, (bucket[0] + self.window_seconds, key))
            else:
                del self._events[key]

    def _capacity_retry_after_unlocked(self, now: float) -> int:
        """Return when the earliest retained bucket can be reclaimed."""
        if self._expiry:
            return max(1, math.ceil(self._expiry[0][0] - now))
        return max(1, math.ceil(self.window_seconds))

    def check(self, ip: str, route: str, *, now: float | None = None) -> tuple[bool, int]:
        """Return ``(allowed, retry_after_seconds)``. Consumes a slot when allowed."""
        ts = float(time.time() if now is None else now)
        key = self._key(ip or "unknown", route)
        with self._lock:
            cutoff = ts - self.window_seconds
            self._prune_expired_unlocked(cutoff)
            bucket = self._events.get(key)
            if bucket is None:
                if len(self._events) >= self.max_keys:
                    return False, self._capacity_retry_after_unlocked(ts)
                bucket = deque[float]()
                self._events[key] = bucket
            if len(bucket) >= self.limit:
                oldest = bucket[0]
                retry_after = max(1, int(self.window_seconds - (ts - oldest) + 0.999))
                return False, retry_after
            bucket.append(ts)
            if len(bucket) == 1:
                heappush(self._expiry, (ts + self.window_seconds, key))
            return True, 0

    def check_request(
        self,
        request: Request,
        *,
        route: str | None = None,
        now: float | None = None,
    ) -> None:
        """Raise ``HTTPException`` 429 with ``Retry-After`` when limited."""
        client = _client_ip_for_rate_limit(request)
        path = route if route is not None else request.url.path
        allowed, retry_after = self.check(client, path, now=now)
        if not allowed:
            raise auth_rate_limit_exception(retry_after)


def auth_rate_limit_dependency(
    limiter: AuthRateLimiter,
    *,
    route: str | None = None,
) -> Callable[..., Any]:
    """FastAPI dependency factory that applies ``limiter`` to the request."""

    def _dependency(request: Request) -> None:
        limiter.check_request(request, route=route)

    return _dependency
