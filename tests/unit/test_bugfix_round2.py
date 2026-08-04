"""Regression tests for the second top-20 severity bug-fix pass."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from jinja2 import DictLoader, Environment
from starlette.requests import Request

from hedron.cache import cache_data
from hedron.preload import evaluate_preload_request
from hedron.streaming import StreamingComponentResponse
from hedron_charts.limits import reject_active_svg
from hedron_core.cache import build_cache_key, get_cache_traces, reset_cache_for_tests
from hedron_core.channel import ChannelBudget, PageSessionChannel
from hedron_core.diagnostics import HedronError
from hedron_core.htmx_contract import approved_headers, is_local_path, safe_css_selector
from hedron_core.icons import clear_icons_for_tests, register_icon
from hedron_core.interaction import InteractionResult, interaction_headers
from hedron_core.jobs import RedisJobBackend
from hedron_core.preload import NavigationPreloadPolicy
from hedron_core.security import TrustedHtml
from hedron_data.memory import InMemoryDataSource
from hedron_data.sources import CellUpdate, DataChanges, DataQuery
from hedron_jinja import HedronJinja


def _http_request(
    *, origin: str | None = None, host: str = "example.test", port: int = 80
) -> Request:
    headers: list[tuple[bytes, bytes]] = []
    if origin is not None:
        headers.append((b"origin", origin.encode("ascii")))
    return Request(
        {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": "/",
            "raw_path": b"/",
            "query_string": b"",
            "headers": headers,
            "client": ("127.0.0.1", 123),
            "server": (host, port),
        }
    )


def test_reject_active_svg_blocks_data_and_smuggled_javascript() -> None:
    with pytest.raises(HedronError) as exc:
        reject_active_svg('<svg><a href="data:text/html;base64,PHNjcmlwdD4=">x</a></svg>')
    assert exc.value.diagnostic.code == "HED-CHART-0006"
    with pytest.raises(HedronError):
        reject_active_svg('<svg><a href="java\nscript:alert(1)">x</a></svg>')


def test_register_icon_blocks_iframe_and_onmouseenter() -> None:
    clear_icons_for_tests()
    with pytest.raises(HedronError) as exc:
        register_icon("bad", "<svg><iframe src='x'></iframe></svg>", title="Bad")
    assert exc.value.diagnostic.code == "HED-ICON-0003"
    with pytest.raises(HedronError):
        register_icon("hover", '<svg onmouseenter="alert(1)"></svg>', title="Hover")


def test_build_cache_key_rejects_starlette_request() -> None:
    request = _http_request()
    with pytest.raises(ValueError, match="Request"):
        build_cache_key(identity="i", args=(request,))


def test_sensitive_cache_rejects_missing_vary_on() -> None:
    reset_cache_for_tests()

    @cache_data(scope="user", vary_on=("user_id",), ttl=60)
    def from_context() -> str:
        return "secret-for-alice"

    assert from_context() == "secret-for-alice"
    traces = get_cache_traces()
    assert any(t.kind == "reject" for t in traces)


def test_is_local_path_rejects_double_encoded_traversal() -> None:
    assert is_local_path("/..%252f..%252fevil") is False
    assert is_local_path("/..;/etc") is False


def test_approved_headers_location_and_reswap_validation() -> None:
    with pytest.raises(ValueError, match="Unapproved HX-Location"):
        approved_headers(location={"path": "/ok", "headers": {"Authorization": "x"}})
    with pytest.raises(ValueError, match="target"):
        approved_headers(location={"path": "/ok", "target": "javascript:alert(1)"})
    with pytest.raises(ValueError, match="reswap"):
        approved_headers(reswap='innerHTML" onload="x')
    headers = approved_headers(location={"path": "/ok", "target": "#main", "swap": "outerHTML"})
    assert "HX-Location" in headers
    assert safe_css_selector("[onclick=x]") is False


def test_redis_job_submit_fail_closed_when_winner_missing() -> None:
    client = MagicMock()
    client.get.return_value = None
    client.set.return_value = False
    client.delete.return_value = 1
    backend = RedisJobBackend(client)
    with pytest.raises(RuntimeError, match="winner record"):
        backend.submit("demo", {}, idempotency_key="k1")


def test_websocket_budget_fields_exposed() -> None:
    channel = PageSessionChannel(
        channel_id="c1",
        declared_regions=frozenset({"main"}),
        budget=ChannelBudget(max_message_bytes=16, max_messages=2, idle_timeout_seconds=1.0),
    )
    assert channel.budget.max_message_bytes == 16
    assert channel.budget.max_messages == 2


def test_safe_download_rejects_path_escape(tmp_path: Path) -> None:
    from hedron.builtins.files import safe_download_response

    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "secret.txt"
    outside.write_text("nope", encoding="utf-8")
    with pytest.raises(PermissionError, match="escapes"):
        safe_download_response(outside, root=root, filename="secret.txt", authorized=True)


def test_job_sse_authz_mismatch() -> None:
    from fastapi import FastAPI
    from starlette.testclient import TestClient

    from hedron.sse import job_status_sse_response
    from hedron_core.jobs import InMemoryJobBackend, JobState, set_job_backend

    backend = InMemoryJobBackend()
    set_job_backend(backend)
    handle = backend.submit("t", {}, auth_subject="alice", tenant_id="t1")

    app = FastAPI()

    @app.get("/sse")
    def _endpoint():
        return job_status_sse_response(
            handle.job_id,
            backend=backend,
            auth_subject="bob",
            tenant_id="t1",
            poll_interval_seconds=0.01,
        )

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/sse")
    assert response.status_code == 403
    status = backend.get(handle.job_id)
    assert status is not None
    assert status.state is JobState.QUEUED


def test_preload_same_origin_requires_full_match() -> None:
    policy = NavigationPreloadPolicy(enabled=True, only_same_origin=True)
    missing = evaluate_preload_request(_http_request(origin=None), policy)
    assert missing.allowed is False
    cross_port = evaluate_preload_request(
        _http_request(origin="http://example.test:8080", host="example.test", port=80),
        policy,
    )
    assert cross_port.allowed is False
    same = evaluate_preload_request(
        _http_request(origin="http://example.test", host="example.test", port=80),
        policy,
    )
    assert same.allowed is True


def test_inmemory_writable_fields_deny_by_default() -> None:
    src = InMemoryDataSource([{"id": "1", "name": "Ada", "role": "admin"}])
    result = src.apply(DataChanges(updates=(CellUpdate(row_key="1", field="role", value="user"),)))
    assert result.ok is False
    assert src.fetch(DataQuery()).rows[0]["role"] == "admin"


def test_hdj_forces_autoescape_when_strict_false() -> None:
    source = '---hdj\nversion = 1\nkind = "fragment"\nprofile = "standard"\n---\n{{ view.x }}'
    env = Environment(loader=DictLoader({"x.hdj": source}))
    env.autoescape = False
    templates = HedronJinja(env, strict=False)
    assert templates.environment.autoescape is True
    out = templates.render("x.hdj", {"x": "<em>x</em>"})
    assert "&lt;em&gt;" in out.html


def test_stream_region_id_rejects_crlf() -> None:
    with pytest.raises(ValueError, match="control"):
        StreamingComponentResponse(iter([b"x"]), region_id="main\r\nX-Injected: 1")


def test_interaction_cache_none_still_emits_vary() -> None:
    headers = interaction_headers(InteractionResult(cache=None))
    assert "Cache-Control" not in headers
    assert "HX-Request" in headers["Vary"]
    assert "HX-History-Restore-Request" in headers["Vary"]


def test_highlight_code_without_nh3_escapes(monkeypatch: pytest.MonkeyPatch) -> None:
    import hedron.content as content

    monkeypatch.setattr(content, "_nh3_available", lambda: False)
    trusted: TrustedHtml = content.highlight_code("<script>alert(1)</script>", lexer="text")
    assert "<script>" not in trusted.value
    assert "&lt;script&gt;" in trusted.value


def test_matplotlib_png_alt_escaped() -> None:
    import html as html_stdlib

    from hedron_charts.adapters import MatplotlibAdapter
    from hedron_core import render
    from hedron_core.visualization import ChartAccessibility, ChartOutput

    adapter = MatplotlibAdapter()
    node = adapter.render_node(
        ChartOutput(
            kind="png",
            body="AAAA",
            accessibility=ChartAccessibility(
                title="t",
                alt='"><img src=x onerror=alert(1)>',
                description="d",
            ),
        )
    )
    out = render(node).html
    assert "<img src=x" not in out
    assert html_stdlib.escape('"><img src=x onerror=alert(1)>', quote=True) in out
