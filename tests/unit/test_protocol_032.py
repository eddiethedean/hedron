"""PROTOCOL-032: Streamable HTTP + SDK matrix."""

from __future__ import annotations

import json

from starlette.applications import Starlette
from starlette.testclient import TestClient

from hedron_mcp import (
    SDK_PIN,
    SUPPORTED_CLIENTS,
    SUPPORTED_PROTOCOL_VERSIONS,
    McpProjection,
    McpResource,
    McpTool,
    mount_mcp,
    negotiate_protocol_version,
    sdk_version,
)


def test_sdk_pin_importable() -> None:
    assert SDK_PIN.startswith(">=")
    ver = sdk_version()
    assert ver
    assert SUPPORTED_CLIENTS
    assert "2025-03-26" in SUPPORTED_PROTOCOL_VERSIONS
    assert negotiate_protocol_version("nope") in SUPPORTED_PROTOCOL_VERSIONS


def test_streamable_http_initialize_and_empty_lists() -> None:
    app = Starlette()
    projection = McpProjection(
        enabled=True,
        principal_resolver=lambda _req: "alice",
    )
    mount_mcp(app, projection, path="/mcp")
    assert projection._mounted is True

    client = TestClient(app)
    init = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {"experimental": {"vendorX": True}},
                "clientInfo": {"name": "pytest", "version": "0"},
            },
        },
        headers={"x-hedron-principal": "alice"},
    )
    assert init.status_code == 200
    body = init.json()
    assert body["result"]["protocolVersion"] == "2025-03-26"
    assert init.headers.get("mcp-session-id")

    listed = client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        headers={"x-hedron-principal": "alice"},
    )
    assert listed.status_code == 200
    assert listed.json()["result"]["tools"] == []


def test_read_resource_and_read_only_tool() -> None:
    app = Starlette()

    def _allow(**_kwargs: object) -> None:
        return None

    projection = McpProjection(
        enabled=True,
        principal_resolver=lambda _req: "alice",
        authz_hook=_allow,
    )
    projection.register_resource(
        McpResource(
            uri="hedron://page/home",
            name="home",
            description="Home",
            reader=lambda uri, _p: {
                "text": json.dumps({"uri": uri}),
                "mimeType": "application/json",
            },
        )
    )
    projection.register_tool(
        McpTool(
            name="status",
            schema={"type": "object", "properties": {}},
            mutate=False,
            handler=lambda: {"ok": True},
        )
    )
    mount_mcp(app, projection)
    client = TestClient(app)
    headers = {"x-hedron-principal": "alice"}

    read = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 3,
            "method": "resources/read",
            "params": {"uri": "hedron://page/home"},
        },
        headers=headers,
    )
    assert read.status_code == 200
    assert "hedron://page/home" in read.json()["result"]["contents"][0]["text"]

    call = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "status", "arguments": {}},
        },
        headers=headers,
    )
    assert call.status_code == 200
    assert call.json()["result"]["isError"] is False
