"""Authlib/FastAPI security conveniences without owning identity."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI, Request
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import ASGIApp

from hedron_core.diagnostics import error

__all__ = [
    "OAuthHelper",
    "create_oauth_client",
    "install_authenticated_from_session",
    "mark_authenticated",
    "require_authlib",
]


def require_authlib() -> Any:
    try:
        import authlib
        from authlib.integrations.starlette_client import OAuth
    except ImportError as exc:
        raise error(
            "HED-AUTH-0001",
            title="auth extra not installed",
            explanation="Authlib helpers require the authlib package.",
            remediation='Install with: pip install "hedron[auth]"',
        ) from exc
    return authlib, OAuth


def create_oauth_client(**kwargs: Any) -> Any:
    """Create an Authlib OAuth registry for Starlette/FastAPI apps."""
    _, OAuth = require_authlib()
    return OAuth(**kwargs)


class OAuthHelper:
    """Thin wrapper documenting Hedron's non-ownership of identity."""

    def __init__(self, oauth: Any | None = None) -> None:
        self.oauth = oauth or create_oauth_client()

    def register(self, name: str, **kwargs: Any) -> Any:
        """Register a provider; applications remain responsible for sessions/claims."""
        return self.oauth.register(name=name, **kwargs)


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
        session = getattr(request, "session", None)
        if isinstance(session, Mapping):
            subject = session.get(self.session_key)
            # Require a non-empty string subject — truthy placeholders must not
            # flip hedron_authenticated (cache / Explorer secured defaults).
            if isinstance(subject, str) and subject.strip():
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

    The session value for ``session_key`` must be a non-empty string subject id.
    """

    app.user_middleware.append(
        Middleware(_AuthenticatedFromSessionMiddleware, session_key=session_key)
    )
    app.middleware_stack = None
