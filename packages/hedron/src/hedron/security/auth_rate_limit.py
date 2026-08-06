"""In-memory auth-endpoint rate limiting with 429 + Retry-After helpers.

Keyed by IP + route. This process-local sliding window is complementary to
ingress throttling: it does **not** coordinate across multiple workers or
hosts. Prefer edge/WAF limits for production multi-worker deployments; use
this helper for single-process demos and defense-in-depth near login routes.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable
from typing import Any

from fastapi import HTTPException, Request, status
from starlette.responses import JSONResponse, Response

__all__ = [
    "AuthRateLimiter",
    "auth_rate_limit_dependency",
    "auth_rate_limit_exception",
    "auth_rate_limit_response",
]


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

    Multi-worker note: each process keeps its own counters. Do not rely on this
    alone for horizontally scaled auth endpoints.
    """

    def __init__(self, *, limit: int = 10, window_seconds: float = 60.0) -> None:
        if limit < 1:
            raise ValueError("limit must be >= 1")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be > 0")
        self.limit = int(limit)
        self.window_seconds = float(window_seconds)
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def _key(self, ip: str, route: str) -> str:
        return f"{ip}\0{route}"

    def check(self, ip: str, route: str, *, now: float | None = None) -> tuple[bool, int]:
        """Return ``(allowed, retry_after_seconds)``. Consumes a slot when allowed."""
        ts = float(time.time() if now is None else now)
        key = self._key(ip or "unknown", route)
        with self._lock:
            bucket = self._events[key]
            cutoff = ts - self.window_seconds
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()
            if len(bucket) >= self.limit:
                oldest = bucket[0]
                retry_after = max(1, int(self.window_seconds - (ts - oldest) + 0.999))
                return False, retry_after
            bucket.append(ts)
            return True, 0

    def check_request(
        self,
        request: Request,
        *,
        route: str | None = None,
        now: float | None = None,
    ) -> None:
        """Raise ``HTTPException`` 429 with ``Retry-After`` when limited."""
        client = request.client.host if request.client else "unknown"
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
