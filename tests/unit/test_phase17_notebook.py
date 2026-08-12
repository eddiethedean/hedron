"""Phase 0.17 notebook preview helper (NOTEBOOK-017)."""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest
from httpx import ASGITransport, AsyncClient

from hedron_notebook import (
    PREVIEW_TOKEN_COOKIE,
    PREVIEW_TOKEN_HEADER,
    PREVIEW_TOKEN_QUERY,
    NotebookPreview,
    PreviewTokenGate,
    __version__,
    start_preview,
    wrap_preview_app,
)


@dataclass
class _FakeServer:
    port: int = 8765
    started: bool = field(default=False, init=False)
    shut_down: bool = field(default=False, init=False)

    def start(self) -> None:
        self.started = True

    def shutdown(self) -> None:
        self.shut_down = True


async def _ok_app(scope: dict[str, object], receive: object, send: object) -> None:
    assert callable(send)
    await send(  # type: ignore[misc]
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [(b"content-type", b"text/plain")],
        }
    )
    await send({"type": "http.response.body", "body": b"ok"})  # type: ignore[misc]


def test_package_version_and_exports() -> None:
    assert __version__ == "0.1.0"
    assert callable(start_preview)
    assert NotebookPreview is not None
    assert callable(wrap_preview_app)
    assert PreviewTokenGate is not None
    assert PREVIEW_TOKEN_QUERY == "hedron_preview_token"
    assert PREVIEW_TOKEN_HEADER == "x-hedron-preview-token"
    assert PREVIEW_TOKEN_COOKIE == "hedron_preview_token"


def test_localhost_preview_token_and_url() -> None:
    server = _FakeServer(port=9123)
    preview = start_preview(
        object(),
        host="127.0.0.1",
        server=server,
        token="test-token-abc",
        root_path="/proxy",
    )
    try:
        assert server.started
        assert preview.hosted_warning is False
        assert preview.port == 9123
        assert preview.token == "test-token-abc"
        assert "hedron_preview_token=test-token-abc" in preview.url
        assert preview.url.startswith("http://127.0.0.1:9123/proxy/?")
        assert preview.external_url() == preview.url
        assert isinstance(preview._app, PreviewTokenGate)
        html = preview.iframe_html(width="80%", height="400")
        assert 'src="http://127.0.0.1:9123/proxy/?hedron_preview_token=test-token-abc"' in html
        assert 'width="80%"' in html
        assert 'height="400"' in html
        assert "sandbox=" in html
    finally:
        preview.shutdown()
    assert server.shut_down


def test_random_token_when_not_provided() -> None:
    server = _FakeServer()
    preview = start_preview(object(), server=server)
    try:
        assert len(preview.token) >= 16
        assert preview.token in preview.url
        assert preview.hosted_warning is False
    finally:
        preview.shutdown()


def test_empty_token_rejected() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        start_preview(object(), server=_FakeServer(), token="")


def test_non_loopback_host_refused() -> None:
    server = _FakeServer()
    with pytest.raises(ValueError, match="refuses non-loopback"):
        start_preview(object(), host="0.0.0.0", server=server)


def test_shutdown_is_idempotent() -> None:
    server = _FakeServer()
    preview = start_preview(object(), server=server)
    preview.shutdown()
    preview.shutdown()
    assert server.shut_down


@pytest.mark.anyio
async def test_preview_token_gate_rejects_missing_and_wrong_token() -> None:
    gated = wrap_preview_app(_ok_app, "secret-token")
    transport = ASGITransport(app=gated)
    async with AsyncClient(transport=transport, base_url="http://preview.test") as client:
        missing = await client.get("/")
        assert missing.status_code == 401
        assert missing.json()["detail"] == "Preview token required"

        wrong = await client.get("/", params={PREVIEW_TOKEN_QUERY: "nope-token-xx"})
        assert wrong.status_code == 401

        ok_query = await client.get("/", params={PREVIEW_TOKEN_QUERY: "secret-token"})
        assert ok_query.status_code == 200
        assert ok_query.text == "ok"
        set_cookie = ok_query.headers.get("set-cookie", "")
        assert f"{PREVIEW_TOKEN_COOKIE}=secret-token" in set_cookie
        assert "HttpOnly" in set_cookie
        assert "SameSite=Lax" in set_cookie

        ok_header = await client.get("/", headers={PREVIEW_TOKEN_HEADER: "secret-token"})
        assert ok_header.status_code == 200
        assert ok_header.text == "ok"
        assert PREVIEW_TOKEN_COOKIE in ok_header.headers.get("set-cookie", "")


@pytest.mark.anyio
async def test_preview_token_cookie_authorizes_follow_up_requests() -> None:
    """Iframe assets/HTMX must work after the first query-auth seeds a cookie."""
    gated = wrap_preview_app(_ok_app, "cookie-token")
    transport = ASGITransport(app=gated)
    async with AsyncClient(transport=transport, base_url="http://preview.test") as client:
        first = await client.get("/", params={PREVIEW_TOKEN_QUERY: "cookie-token"})
        assert first.status_code == 200
        follow = await client.get("/fragment")
        assert follow.status_code == 200
        assert follow.text == "ok"


@pytest.mark.anyio
async def test_start_preview_wraps_app_with_token_gate() -> None:
    preview = start_preview(
        _ok_app,
        server=_FakeServer(),
        token="gate-token-1",
    )
    try:
        assert isinstance(preview._app, PreviewTokenGate)
        transport = ASGITransport(app=preview._app)
        async with AsyncClient(transport=transport, base_url="http://preview.test") as client:
            denied = await client.get("/")
            assert denied.status_code == 401
            allowed = await client.get("/", params={PREVIEW_TOKEN_QUERY: preview.token})
            assert allowed.status_code == 200
            follow = await client.get("/assets/app.js")
            assert follow.status_code == 200
    finally:
        preview.shutdown()
