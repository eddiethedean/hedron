"""Security header middleware."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from hedron.security.policy import SecurityPolicy


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, policy: SecurityPolicy) -> None:
        super().__init__(app)
        self.policy = policy

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        authenticated = bool(getattr(request.state, "hedron_authenticated", False))
        is_htmx = (request.headers.get("HX-Request") or "").lower() == "true"
        for key, value in self.policy.response_headers(authenticated=authenticated).items():
            # Authenticated responses must not remain publicly cacheable even if the
            # app already set a weaker Cache-Control.
            if (authenticated and key in {"Cache-Control", "Pragma"}) or (
                key not in response.headers
            ):
                response.headers[key] = value
        # HTMX / fragment responses must not stay Cache-Control: public.
        if is_htmx:
            existing = response.headers.get("Cache-Control", "")
            if "public" in existing.lower() or not existing:
                response.headers["Cache-Control"] = "private, no-store"
        return response
