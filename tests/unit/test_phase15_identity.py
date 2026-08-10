"""Phase 0.15 M7 identity / session helper tests."""

from __future__ import annotations

import base64
import hashlib

import pytest
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request as StarletteRequest

from hedron.auth import install_authenticated_from_session, mark_authenticated
from hedron.oidc import (
    OidcClientConfig,
    generate_nonce,
    generate_pkce,
    generate_state,
    normalize_claims,
    redact_claims,
    validate_callback_nonce,
    validate_callback_state,
)
from hedron.security.auth_rate_limit import (
    AuthRateLimiter,
    auth_rate_limit_exception,
    auth_rate_limit_response,
)
from hedron.security.login_csrf import (
    LOGIN_CSRF_KEY,
    issue_login_csrf,
    sign_login_csrf,
    validate_login_csrf,
)
from hedron.security.session_timeout import (
    SESSION_CREATED_KEY,
    SESSION_LAST_SEEN_KEY,
    SessionTimeoutError,
    check_session_timeout,
    touch_session,
)
from hedron.security.trusted_header import TrustedHeaderIdentity


def _request(
    *,
    path: str = "/",
    method: str = "GET",
    client_host: str = "127.0.0.1",
    headers: list[tuple[bytes, bytes]] | None = None,
) -> StarletteRequest:
    hdrs = list(headers or [])
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "path": path,
        "raw_path": path.encode(),
        "root_path": "",
        "scheme": "http",
        "server": ("test", 80),
        "client": (client_host, 12345),
        "headers": hdrs,
        "query_string": b"",
    }
    return StarletteRequest(scope)


def test_pkce_and_state_helpers() -> None:
    state = generate_state()
    nonce = generate_nonce()
    pkce = generate_pkce()
    assert state and nonce and pkce.verifier and pkce.challenge
    assert pkce.method == "S256"
    digest = hashlib.sha256(pkce.verifier.encode("ascii")).digest()
    expected = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    assert pkce.challenge == expected

    validate_callback_state(expected=state, received=state)
    validate_callback_nonce(expected=nonce, received=nonce)
    with pytest.raises(ValueError):
        validate_callback_state(expected=state, received="other")
    with pytest.raises(ValueError):
        validate_callback_nonce(expected=nonce, received=None)

    claims = normalize_claims(
        {
            "sub": "user-1",
            "email": "ada@example.com",
            "name": "Ada",
            "access_token": "secret-token",
        }
    )
    redacted = redact_claims(claims)
    assert redacted["sub"] == "user-1"
    assert redacted["email"] == "a***@example.com"
    assert redacted["raw"]["access_token"] == "[redacted]"

    config = OidcClientConfig(
        issuer="https://idp.example/",
        client_id="client",
        redirect_uri="https://app.example/callback",
    )
    assert config.resolved_authorize_url().endswith("/authorize")


def test_login_csrf_roundtrip_session_and_cookie() -> None:
    session: dict = {}
    token = issue_login_csrf(session)
    assert session[LOGIN_CSRF_KEY] == token
    validate_login_csrf(token, session=session)

    secret = "test-secret-key"
    signed = sign_login_csrf(token, secret)
    validate_login_csrf(token, cookie=signed, secret=secret)

    with pytest.raises(HTTPException) as exc:
        validate_login_csrf("wrong", session=session)
    assert exc.value.status_code == 403

    with pytest.raises(HTTPException):
        validate_login_csrf(token, cookie="not-signed", secret=secret)


def test_session_timeout_idle_and_absolute() -> None:
    session: dict = {}
    touch_session(session, now=1_000.0)
    assert session[SESSION_CREATED_KEY] == 1_000.0
    assert session[SESSION_LAST_SEEN_KEY] == 1_000.0

    assert check_session_timeout(
        session,
        idle_seconds=100,
        absolute_seconds=1_000,
        now=1_050.0,
    )

    with pytest.raises(SessionTimeoutError) as idle_exc:
        check_session_timeout(
            session,
            idle_seconds=10,
            absolute_seconds=None,
            now=1_020.0,
        )
    assert idle_exc.value.reason == "idle"

    assert (
        check_session_timeout(
            session,
            idle_seconds=10,
            absolute_seconds=None,
            now=1_020.0,
            raise_on_expired=False,
        )
        is False
    )

    with pytest.raises(SessionTimeoutError) as abs_exc:
        check_session_timeout(
            session,
            idle_seconds=None,
            absolute_seconds=50,
            now=1_060.0,
        )
    assert abs_exc.value.reason == "absolute"


def test_auth_rate_limit_returns_429_with_retry_after() -> None:
    limiter = AuthRateLimiter(limit=2, window_seconds=60.0)
    assert limiter.check("1.2.3.4", "/login", now=1.0)[0] is True
    assert limiter.check("1.2.3.4", "/login", now=2.0)[0] is True
    allowed, retry_after = limiter.check("1.2.3.4", "/login", now=3.0)
    assert allowed is False
    assert retry_after >= 1

    exc = auth_rate_limit_exception(retry_after)
    assert exc.status_code == 429
    assert exc.headers is not None
    assert exc.headers["Retry-After"] == str(max(1, retry_after))

    response = auth_rate_limit_response(7)
    assert response.status_code == 429
    assert response.headers["Retry-After"] == "7"

    # Different route / IP still allowed
    assert limiter.check("1.2.3.4", "/other", now=3.0)[0] is True
    assert limiter.check("9.9.9.9", "/login", now=3.0)[0] is True

    request = _request(path="/login", client_host="1.2.3.4")
    with pytest.raises(HTTPException) as limited:
        limiter.check_request(request, now=4.0)
    assert limited.value.status_code == 429


def test_trusted_header_allow_and_deny() -> None:
    adapter = TrustedHeaderIdentity(["10.0.0.1", "10.0.0.2"], "X-Remote-User")
    allowed = _request(
        client_host="10.0.0.1",
        headers=[(b"x-remote-user", b"ada")],
    )
    denied_peer = _request(
        client_host="8.8.8.8",
        headers=[(b"x-remote-user", b"ada")],
    )
    assert adapter.extract(allowed) == "ada"
    assert adapter.extract(denied_peer) is None  # fail closed: header ignored

    dep = adapter.dependency()
    assert dep(allowed) == "ada"
    with pytest.raises(HTTPException) as exc:
        dep(denied_peer)
    assert exc.value.status_code == 401


def test_mark_authenticated_and_session_install() -> None:
    request = _request()
    mark_authenticated(request)
    assert request.state.hedron_authenticated is True
    mark_authenticated(request, value=False)
    assert request.state.hedron_authenticated is False

    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key="test-secret")
    install_authenticated_from_session(app, session_key="user")

    @app.get("/who")
    def who(req: Request) -> dict:
        return {
            "auth": bool(getattr(req.state, "hedron_authenticated", False)),
            "user": req.session.get("user"),
        }

    @app.post("/login")
    def login(req: Request) -> dict:
        req.session["user"] = "ada"
        return {"ok": True}

    client = TestClient(app)
    assert client.get("/who").json()["auth"] is False
    assert client.post("/login").status_code == 200
    body = client.get("/who").json()
    assert body["user"] == "ada"
    assert body["auth"] is True

    # Truthy non-string session values must not flip authentication.
    @app.post("/login-dict")
    def login_dict(req: Request) -> dict:
        req.session["user"] = {"id": "ada"}
        return {"ok": True}

    assert client.post("/login-dict").status_code == 200
    assert client.get("/who").json()["auth"] is False
