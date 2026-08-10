"""Regression tests for the 0.25.2 round-7 top-20 severity bug-fix pass."""

from __future__ import annotations

import asyncio
from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from starlette.requests import Request

from hedron.connections import ConnectionRegistry
from hedron.mount import normalize_mount_path, prefix_local_path
from hedron.sse import SseResponse
from hedron.streaming import StreamingComponentResponse
from hedron_core.builtins.forms import Hx
from hedron_core.channel import PageSessionChannel, RegionUpdate
from hedron_core.diagnostics import HedronError
from hedron_core.interaction import (
    InteractionResult,
    OobUpdate,
    materialize_interaction_nodes,
)
from hedron_core.live import SseEvent
from hedron_core.mount import normalize_mount_path as core_normalize_mount_path
from hedron_core.rendering import render
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_flask.live import sse_response as flask_sse_response
from hedron_flask.responses import _maybe_prepare


def test_normalize_mount_path_rejects_dot_segments() -> None:
    for raw in (
        "/app/../evil",
        "/app/%2e%2e/evil",
        "../evil",
        "/app/./nested",
        "/app/%2e/x",
        "/app//x",
    ):
        assert core_normalize_mount_path(raw) == ""
        assert normalize_mount_path(raw) == ""


def test_prefix_local_path_refuses_dirty_mount_result() -> None:
    # Dirty mounts normalize to empty and leave the local path unchanged.
    assert prefix_local_path("/login", "/app/../evil") == "/login"
    assert prefix_local_path("/login", "/app") == "/app/login"


def test_hx_keeps_safeurl_and_rejects_bare_relative() -> None:
    attrs = Hx(method="post", url="/submit").as_html_attrs()
    assert isinstance(attrs["hx-post"], SafeUrl)
    with pytest.raises(HedronError):
        Hx(method="post", url="submit").as_html_attrs()
    with pytest.raises(HedronError):
        SafeUrl.parse("submit", purpose=UrlPurpose.FORM_ACTION)
    assert SafeUrl.parse("/submit", purpose=UrlPurpose.FORM_ACTION).value == "/submit"


def test_reserved_oob_select_wraps_without_regions() -> None:
    from hedron_core.html import html

    result = InteractionResult(
        content=None,
        oob=(OobUpdate(content=html.span("hi"), select="#hedron-toast"),),
    )
    node = materialize_interaction_nodes(result)
    assert node is not None
    out = render(node).html
    assert 'id="hedron-toast"' in out
    assert "hx-swap-oob" in out


def test_region_update_rejects_unsafe_swap() -> None:
    channel = PageSessionChannel(
        channel_id="c1",
        declared_regions=frozenset({"panel"}),
    )
    with pytest.raises(ValueError, match="Unsafe HTMX swap"):
        channel.encode_region_update(
            RegionUpdate(region_id="panel", html="<div/>", swap="innerHTML onload=x")
        )


def test_sse_and_stream_force_no_store_after_caller_headers() -> None:
    def _empty() -> Iterator[bytes]:
        if False:
            yield b""

    sse = SseResponse(_empty(), headers={"Cache-Control": "public, max-age=60"})
    assert sse.headers["cache-control"] == "no-store"
    stream = StreamingComponentResponse(
        _empty(),
        region_id="panel",
        headers={"Cache-Control": "public, s-maxage=30"},
    )
    assert stream.headers["cache-control"] == "no-store"


def test_flask_sse_rejects_raw_strings() -> None:
    with pytest.warns(DeprecationWarning):
        response = flask_sse_response([SseEvent(data="ok")])
    body = "".join(response.response)  # type: ignore[attr-defined]
    assert "data:" in body
    with pytest.warns(DeprecationWarning):
        bad = flask_sse_response(["event: inject\ndata: x\n\n"])  # type: ignore[list-item]
    with pytest.raises(TypeError, match="SseEvent"):
        "".join(bad.response)  # type: ignore[attr-defined]


def test_maybe_prepare_fail_closed_under_running_loop() -> None:
    async def _probe() -> None:
        with pytest.raises(RuntimeError, match="event loop is already running"):
            _maybe_prepare("not-a-render-result")  # type: ignore[arg-type]

    asyncio.run(_probe())


def test_sync_connection_dispose_fail_closed_on_awaitable() -> None:
    class _AsyncConn:
        async def close(self) -> None:
            return None

    registry = ConnectionRegistry()
    registry.register("db", factory=lambda: _AsyncConn())
    registry.get("db")
    with pytest.raises(RuntimeError, match="close_all_async"):
        registry.close_all()


def test_session_auth_requires_nonempty_string(monkeypatch: pytest.MonkeyPatch) -> None:
    from fastapi import FastAPI
    from starlette.middleware.sessions import SessionMiddleware

    from hedron.auth import install_authenticated_from_session

    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key="test-secret")
    install_authenticated_from_session(app, session_key="user")

    @app.get("/who")
    def who(req: Request) -> dict[str, Any]:
        return {"auth": bool(getattr(req.state, "hedron_authenticated", False))}

    @app.post("/login")
    def login(req: Request) -> dict[str, str]:
        req.session["user"] = "   "
        return {"ok": "1"}

    client = TestClient(app)
    assert client.post("/login").status_code == 200
    assert client.get("/who").json()["auth"] is False
