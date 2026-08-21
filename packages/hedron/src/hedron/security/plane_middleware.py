"""FastAPI request-plane middleware: SecurityContext + RequestBudget."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from hedron_core.request_plane import (
    RequestSecurityBinding,
    bind_request_security,
    unbind_request_security,
)
from hedron_core.security_policy import SecurityPolicy


class SecurityPlaneMiddleware(BaseHTTPMiddleware):
    """Install ContextVar security plane before handlers; tear down after."""

    def __init__(
        self,
        app: ASGIApp,
        policy: SecurityPolicy,
        *,
        application_id: str = "hedron",
    ) -> None:
        super().__init__(app)
        self.policy = policy
        self.application_id = application_id

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        binding: RequestSecurityBinding = bind_request_security(
            policy=self.policy,
            application_id=self.application_id,
            correlation_id=request.headers.get("x-request-id", ""),
        )
        request.state.hedron_security_binding = binding
        try:
            return await call_next(request)
        finally:
            unbind_request_security(binding)
