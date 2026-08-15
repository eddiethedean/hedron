"""Authlib/FastAPI security conveniences without owning identity."""

from __future__ import annotations

from hedron.auth.oauth import OAuthHelper as OAuthHelper
from hedron.auth.oauth import create_oauth_client as create_oauth_client
from hedron.auth.oauth import require_authlib as require_authlib
from hedron.auth.session import (
    install_authenticated_from_session as install_authenticated_from_session,
)
from hedron.auth.session import mark_authenticated as mark_authenticated

__all__ = [
    "OAuthHelper",
    "create_oauth_client",
    "install_authenticated_from_session",
    "mark_authenticated",
    "require_authlib",
]
