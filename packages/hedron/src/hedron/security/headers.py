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
        for key, value in self.policy.response_headers(authenticated=authenticated).items():
            if key not in response.headers:
                response.headers[key] = value
        return response
