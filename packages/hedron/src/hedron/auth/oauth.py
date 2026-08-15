"""Authlib OAuth conveniences without owning identity."""

from __future__ import annotations

from typing import Any

from hedron_core.diagnostics import error

__all__ = [
    "OAuthHelper",
    "create_oauth_client",
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
