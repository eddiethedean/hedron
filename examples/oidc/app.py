"""Provider-neutral OIDC authorization-code flow for Hedron and Authlib."""

from __future__ import annotations

import os
from collections.abc import Mapping

from authlib.integrations.base_client.errors import OAuthError
from fastapi import Request, status
from fastapi.responses import RedirectResponse

from hedron import Alert, Hedron, Link, Page, Stack, Text
from hedron.auth import create_oauth_client, install_authenticated_from_session
from hedron.oidc import normalize_claims


def required_setting(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Set {name} before starting the OIDC example")
    return value


OIDC_ISSUER = required_setting("OIDC_ISSUER").rstrip("/")
OIDC_CLIENT_ID = required_setting("OIDC_CLIENT_ID")
OIDC_CLIENT_SECRET = required_setting("OIDC_CLIENT_SECRET")
OIDC_REDIRECT_URI = os.environ.get("OIDC_REDIRECT_URI", "http://127.0.0.1:8000/auth/callback")

app = Hedron(
    title="OIDC example",
    security="standard",
    explorer="off",
    session_secret=required_setting("SESSION_SECRET"),
)
install_authenticated_from_session(app, session_key="oidc_sub")

oauth = create_oauth_client()
provider = oauth.register(
    name="provider",
    client_id=OIDC_CLIENT_ID,
    client_secret=OIDC_CLIENT_SECRET,
    server_metadata_url=f"{OIDC_ISSUER}/.well-known/openid-configuration",
    client_kwargs={"scope": "openid profile email"},
)


@app.get("/login")
async def login(request: Request) -> RedirectResponse:
    """Start authorization; Authlib stores and later validates state in the session."""
    return await provider.authorize_redirect(request, OIDC_REDIRECT_URI)


@app.get("/auth/callback")
async def auth_callback(request: Request) -> RedirectResponse:
    """Exchange the code, validate the ID token, and establish the host session."""
    try:
        token = await provider.authorize_access_token(request)
    except OAuthError:
        request.session.clear()
        return RedirectResponse("/?error=oidc", status_code=status.HTTP_303_SEE_OTHER)

    raw_claims = token.get("userinfo")
    if not isinstance(raw_claims, Mapping):
        raw_claims = await provider.userinfo(token=token)
    claims = normalize_claims(raw_claims)

    # Keep only the small identity projection needed by the UI. Never put access,
    # refresh, or ID tokens into Hedron's signed cookie session.
    request.session.clear()
    request.session["oidc_sub"] = claims.sub
    request.session["oidc_name"] = claims.name or claims.email or claims.sub
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@app.page("/")
def home(request: Request, error: str | None = None) -> Page:
    subject = request.session.get("oidc_sub")
    if not subject:
        feedback = (
            Alert(
                "The identity provider did not complete sign-in. Try again.",
                title="Sign-in failed",
                tone="danger",
            )
            if error == "oidc"
            else None
        )
        return Page(
            Stack(
                Text("Sign in with the configured OpenID Connect provider."),
                feedback,
                Link("Sign in", "/login"),
            ),
            title="OIDC sign in",
        )

    return Page(
        Stack(
            Text(f"Signed in as {request.session.get('oidc_name', subject)}"),
            logout.button("Sign out"),
        ),
        title="OIDC account",
    )


@app.command("/logout", fallback="/")
def logout(request: Request) -> RedirectResponse:
    """End the local session; add provider end-session redirect if required."""
    request.session.clear()
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
