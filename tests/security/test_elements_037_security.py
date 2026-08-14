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


@pytest.mark.parametrize(
    "attributes",
    [
        {"style": "background:url(javascript:alert(1))"},
        {"href": "vbscript:msgbox(1)"},
        {"src": "data:text/html,alert(1)"},
        {"formaction": "vbscript:msgbox(1)"},
        {"poster": "file:///tmp/x"},
        {"srcdoc": "<script>alert(1)</script>"},
        {"srcset": "javascript:alert(1) 1x"},
    ],
)
def test_markup_rejects_style_and_dangerous_url_schemes(attributes: dict[str, str]) -> None:
    """#244: style / vbscript / data / file / srcdoc must not reach ABI markup."""
    with pytest.raises(HedronError) as exc:
        render_element_markup(
            tag_name="hedron-field-text",
            abi_version=1,
            element_id="hedron-field-text",
            attributes=attributes,
        )
    assert exc.value.diagnostic.code in {"HED-SEC-0003", "HED-SEC-0007"}


def test_markup_allows_layout_style_and_root_relative_urls() -> None:
    html = render_element_markup(
        tag_name="hedron-action-async",
        abi_version=1,
        element_id="hedron-action-async",
        attributes={
            "style": "--hedron-gap: 1rem",
            "hx-post": "/run",
            "href": "/ok",
        },
        server_content="Run",
    )
    assert "--hedron-gap: 1rem" in html
    assert 'hx-post="/run"' in html
    assert 'href="/ok"' in html


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
