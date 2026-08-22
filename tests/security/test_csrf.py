"""CSRF validation fail-path matrix for FastAPI Hedron."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from starlette.requests import Request

from hedron import Hedron, Text
from hedron.security.csrf import prepare_csrf_from_request, validate_csrf
from hedron.security.policy import SecurityPolicy


def _policy() -> SecurityPolicy:
    return SecurityPolicy.from_name("standard")


def _request(
    *,
    method: str = "POST",
    cookie: str | None = "tok",
    header: str | None = None,
    form_token: str | None = None,
) -> Request:
    headers: list[tuple[bytes, bytes]] = [(b"content-type", b"application/x-www-form-urlencoded")]
    if header is not None:
        headers.append((b"x-csrf-token", header.encode()))
    cookies = f"hedron_csrf={cookie}" if cookie else ""
    if cookies:
        headers.append((b"cookie", cookies.encode()))
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "path": "/act",
        "raw_path": b"/act",
        "root_path": "",
        "scheme": "http",
        "server": ("test", 80),
        "client": ("test", 123),
        "headers": headers,
        "query_string": b"",
    }
    request = Request(scope)
    if form_token is not None:
        request.state.hedron_csrf_form_token = form_token
    return request


@pytest.mark.security
def test_validate_csrf_requires_matching_cookie_and_header() -> None:
    policy = _policy()
    validate_csrf(_request(cookie="tok", header="tok"), policy)

    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        validate_csrf(_request(cookie="tok", header="other"), policy)
    assert exc.value.status_code == 403

    with pytest.raises(HTTPException):
        validate_csrf(_request(cookie="tok", header=None), policy)

    with pytest.raises(HTTPException):
        validate_csrf(_request(cookie=None, header="tok"), policy)


@pytest.mark.security
def test_validate_csrf_accepts_form_token_when_header_absent() -> None:
    policy = _policy()
    validate_csrf(_request(cookie="tok", header=None, form_token="tok"), policy)

    from fastapi import HTTPException

    with pytest.raises(HTTPException):
        validate_csrf(_request(cookie="tok", header=None, form_token="nope"), policy)


@pytest.mark.security
@pytest.mark.anyio
async def test_prepare_csrf_ignores_json_body_token() -> None:
    """JSON bodies must not supply form csrf_token; header is required."""
    policy = _policy()
    headers = [
        (b"content-type", b"application/json"),
        (b"cookie", b"hedron_csrf=tok"),
    ]
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "path": "/act",
        "raw_path": b"/act",
        "root_path": "",
        "scheme": "http",
        "server": ("test", 80),
        "client": ("test", 123),
        "headers": headers,
        "query_string": b"",
    }

    async def receive() -> dict[str, object]:
        return {
            "type": "http.request",
            "body": b'{"csrf_token":"tok","x":1}',
            "more_body": False,
        }

    request = Request(scope, receive)
    await prepare_csrf_from_request(request, policy)
    assert (
        not hasattr(request.state, "hedron_csrf_form_token")
        or getattr(request.state, "hedron_csrf_form_token", None) is None
    )

    from fastapi import HTTPException

    with pytest.raises(HTTPException):
        validate_csrf(request, policy)


@pytest.mark.security
@pytest.mark.anyio
async def test_prepare_csrf_skips_body_without_cookie() -> None:
    policy = _policy()
    request = _request(cookie=None)
    parsed = False

    async def fail_form():
        nonlocal parsed
        parsed = True
        raise AssertionError("form parsing should be skipped")

    request.form = fail_form  # type: ignore[method-assign]
    await prepare_csrf_from_request(request, policy)
    assert parsed is False


@pytest.mark.security
def test_action_csrf_multipart_and_header_mismatch() -> None:
    app = Hedron(title="csrf", security="standard", session_secret="secret", explorer="off")

    @app.page("/")
    def home() -> Text:
        return Text("home")

    @app.action("/act")
    def act() -> Text:
        return Text("ok")

    client = TestClient(app)
    token = client.get("/").cookies.get("hedron_csrf")
    assert token

    denied = client.post("/act", data={"x": "1"})
    assert denied.status_code == 403

    mismatch = client.post(
        "/act",
        data={"x": "1", "csrf_token": token},
        headers={"X-CSRF-Token": "forged"},
    )
    assert mismatch.status_code == 403

    ok_form = client.post("/act", data={"x": "1", "csrf_token": token})
    assert ok_form.status_code == 200
    assert "ok" in ok_form.text

    ok_header = client.post("/act", data={"x": "1"}, headers={"X-CSRF-Token": token})
    assert ok_header.status_code == 200

    files = {"file": ("a.txt", b"hi", "text/plain")}
    ok_mp = client.post(
        "/act",
        data={"csrf_token": token},
        files=files,
    )
    assert ok_mp.status_code == 200
