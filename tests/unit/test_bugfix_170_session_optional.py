"""Regression for #170: optional session reads must not assert without middleware."""

from __future__ import annotations

from fastapi import FastAPI
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.testclient import TestClient

from hedron.auth import install_authenticated_from_session
from hedron.color_mode import read_color_mode_preference
from hedron_core.color_mode import ColorMode
from hedron_mcp import McpProjection, mount_mcp


def test_read_color_mode_preference_without_session_middleware() -> None:
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [],
        "query_string": b"",
    }
    assert read_color_mode_preference(Request(scope)) is ColorMode.SYSTEM


def test_install_authenticated_from_session_without_session_middleware() -> None:
    app = FastAPI()
    install_authenticated_from_session(app)

    @app.get("/")
    def root() -> dict[str, bool]:
        return {"ok": True}

    response = TestClient(app, raise_server_exceptions=False).get("/")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_default_mcp_mount_without_session_middleware_fails_closed() -> None:
    app = Starlette()
    mount_mcp(app, McpProjection(enabled=True))
    response = TestClient(app, raise_server_exceptions=False).post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
    )
    assert response.status_code == 403
    body = response.json()
    assert body["error"]["message"].startswith("MCP authorization requires")
