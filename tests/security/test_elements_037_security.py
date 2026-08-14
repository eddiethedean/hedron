"""SECURITY-037: markup hx-on reject and MCP origin/body bounds."""

from __future__ import annotations

import pytest
from starlette.applications import Starlette
from starlette.testclient import TestClient

from hedron_core.diagnostics import HedronError
from hedron_elements.markup import render_element_markup
from hedron_mcp import McpProjection, mount_mcp


def test_markup_rejects_hx_on_handler() -> None:
    with pytest.raises(HedronError) as exc:
        render_element_markup(
            tag_name="hedron-field-text",
            abi_version=1,
            element_id="hedron-field-text",
            attributes={"onclick": "alert(1)"},
            server_content="x",
        )
    assert exc.value.diagnostic.code == "HED-SEC-0002"


def test_markup_rejects_javascript_in_hx_attr() -> None:
    with pytest.raises(HedronError) as exc:
        render_element_markup(
            tag_name="hedron-action-async",
            abi_version=1,
            element_id="hedron-action-async",
            attributes={"hx-get": "javascript:void(0)"},
            server_content="Run",
        )
    assert exc.value.diagnostic.code == "HED-SEC-0003"


def test_mcp_blocks_origin_when_allowlist_unconfigured() -> None:
    app = Starlette()
    projection = McpProjection(
        enabled=True,
        principal_resolver=lambda _r: "alice",
        allowed_origins=None,
    )
    mount_mcp(app, projection)
    client = TestClient(app)
    blocked = client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
        headers={"x-hedron-principal": "alice", "origin": "https://evil.example"},
    )
    assert blocked.status_code == 403


def test_mcp_rejects_oversized_body() -> None:
    app = Starlette()
    projection = McpProjection(
        enabled=True,
        principal_resolver=lambda _r: "alice",
    )
    projection.bounds.max_request_bytes = 32
    mount_mcp(app, projection)
    client = TestClient(app)
    oversized = client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {"x": "y" * 200}},
        headers={"x-hedron-principal": "alice"},
    )
    assert oversized.status_code == 413
