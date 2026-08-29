"""Session-backed hedron_authenticated signal without owning identity."""

from __future__ import annotations

from fastapi import FastAPI, Request
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import ASGIApp

__all__ = [
    "install_authenticated_from_session",
    "mark_authenticated",
]


def mark_authenticated(request: Request, *, value: bool = True) -> None:
    """Set ``request.state.hedron_authenticated`` for private/no-store cache defaults.

    Mirrors Flask/Django ``AuthSignal`` semantics used by security headers and
    Explorer secured mode. Pass ``value=False`` for an explicit anonymous/public override.
    """
    request.state.hedron_authenticated = bool(value)


class _AuthenticatedFromSessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, session_key: str = "user") -> None:
        super().__init__(app)
        self.session_key = session_key

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Starlette's Request.session asserts when SessionMiddleware is absent;
        # getattr still invokes the property, so gate on scope first (#170).
        if "session" in request.scope:
            session = request.session
            subject = session.get(self.session_key)
            # SessionAuthFlow is generic over its serialized principal. Any
            # non-empty application-owned session value represents a login;
            # strings receive whitespace validation for compatibility.
            authenticated = bool(subject.strip()) if isinstance(subject, str) else bool(subject)
            if authenticated:
                mark_authenticated(request, value=True)
        return await call_next(request)


def install_authenticated_from_session(
    app: FastAPI,
    session_key: str = "user",
) -> None:
    """Auto-wire ``hedron_authenticated`` when the host session has ``session_key``.

    Inserts innermost middleware so ``SessionMiddleware`` has already populated
    ``request.session``. Applications still own login and authorization; this only
    aligns cache/Explorer private defaults with an existing session user.

    The session value for ``session_key`` must be a non-empty serialized principal.
    """

    app.user_middleware.append(
        Middleware(_AuthenticatedFromSessionMiddleware, session_key=session_key)
    )
    app.middleware_stack = None
