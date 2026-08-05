"""Regression tests for the third top-20 severity bug-fix pass."""

from __future__ import annotations

import base64

import pytest
from fastapi import FastAPI, HTTPException
from jinja2 import DictLoader, Environment
from starlette.testclient import TestClient

from hedron.cache import cache_data
from hedron.jobs import job_status_response
from hedron.preload import apply_preload_headers
from hedron.security.policy import SecurityPolicy
from hedron.security.redirects import redirect_external
from hedron.sse import SseResponse, job_status_sse_response
from hedron.streaming import StreamingComponentResponse
from hedron_charts.adapters import MatplotlibAdapter
from hedron_charts.limits import reject_remote_urls
from hedron_core.cache import get_cache_traces, reset_cache_for_tests
from hedron_core.diagnostics import HedronError
from hedron_core.html import html
from hedron_core.htmx_contract import approved_headers
from hedron_core.icons import clear_icons_for_tests, register_icon
from hedron_core.interaction import InteractionResult, interaction_headers
from hedron_core.jobs import InMemoryJobBackend, job_authorized
from hedron_core.preload import PreloadDecision
from hedron_core.rendering import render
from hedron_core.visualization import ChartAccessibility, ChartOutput
from hedron_data.sources import DataQuery
from hedron_jinja import HedronJinja, TemplateSpec


def _hdj(body: str) -> str:
    return f'---hdj\nversion = 1\nkind = "fragment"\nprofile = "standard"\n---\n{body}'


def test_data_aria_attr_name_injection_rejected() -> None:
    with pytest.raises(HedronError) as exc:
        html.div(data={"x onmouseover=alert(1)": "1"})
    assert exc.value.diagnostic.code == "HED-SEC-0010"
    with pytest.raises(HedronError):
        html.div(data={"x><script": "1"})
    with pytest.raises(HedronError):
        html.div(**{"data-x onmouseover": "1"})


def test_meta_refresh_url_with_spaces_rejected() -> None:
    with pytest.raises(HedronError) as exc:
        html.meta(**{"http-equiv": "refresh", "content": "0;url =https://evil.example"})
    assert exc.value.diagnostic.code == "HED-SEC-0008"


def test_job_idempotency_is_tenant_scoped() -> None:
    backend = InMemoryJobBackend()
    a = backend.submit(
        "demo",
        {"secret": 1},
        idempotency_key="shared",
        tenant_id="A",
        auth_subject="alice",
    )
    b = backend.submit(
        "demo",
        {},
        idempotency_key="shared",
        tenant_id="B",
        auth_subject="bob",
    )
    assert a.job_id != b.job_id
    assert backend.request_cancel(a.job_id, auth_subject="bob", tenant_id="B") is False
    assert backend.request_cancel(a.job_id, auth_subject="alice", tenant_id="A") is True


def test_matplotlib_render_node_rejects_active_svg_and_bad_png() -> None:
    adapter = MatplotlibAdapter()
    acc = ChartAccessibility(title="t", alt="a", description="d")
    with pytest.raises(HedronError):
        adapter.render_node(
            ChartOutput(
                kind="svg",
                body='<svg onload="alert(1)"></svg>',
                accessibility=acc,
            )
        )
    with pytest.raises(HedronError):
        adapter.render_node(
            ChartOutput(
                kind="png",
                body='AAAA" onerror="alert(1)',
                accessibility=acc,
            )
        )
    ok_png = base64.b64encode(b"\x89PNG\r\n").decode("ascii")
    node = adapter.render_node(ChartOutput(kind="png", body=ok_png, accessibility=acc))
    out = render(node).html
    assert "onerror" not in out
    assert f"data:image/png;base64,{ok_png}" in out


def test_job_cancel_requires_matching_auth() -> None:
    backend = InMemoryJobBackend()
    handle = backend.submit("t", {}, auth_subject="alice", tenant_id="t1")
    assert backend.request_cancel(handle.job_id) is False
    assert backend.request_cancel(handle.job_id, auth_subject="bob", tenant_id="t1") is False
    assert backend.request_cancel(handle.job_id, auth_subject="alice", tenant_id="t1") is True


def test_private_cache_requires_vary_on() -> None:
    reset_cache_for_tests()

    @cache_data(ttl=30, scope="private")
    def load() -> str:
        return "x"

    assert load() == "x"
    assert any(e.kind == "reject" for e in get_cache_traces())


def test_flask_django_style_auth_cache_header_helpers() -> None:
    from hedron_django.responses import _apply_auth_cache_headers as django_apply
    from hedron_flask.responses import _apply_auth_cache_headers as flask_apply

    flask_headers: dict[str, str] = {}
    django_headers: dict[str, str] = {}
    flask_apply(flask_headers, authenticated=True)
    django_apply(django_headers, authenticated=True)
    assert flask_headers["Cache-Control"] == "private, no-store"
    assert django_headers["Cache-Control"] == "private, no-store"


def test_hdj_rejects_safe_when_strict_false() -> None:
    source = _hdj("{{ view.value|safe }}")
    templates = HedronJinja(Environment(loader=DictLoader({"x.hdj": source})), strict=False)
    diagnostics = templates.check(TemplateSpec("x.hdj", strict=False))
    assert diagnostics
    with pytest.raises(HedronError):
        templates.render(TemplateSpec("x.hdj", strict=False), {"value": "<em>x</em>"})


def test_header_names_reject_controls() -> None:
    with pytest.raises(ValueError, match="control"):
        SseResponse(iter([b"data: x\n\n"]), headers={"X-A\r\nX-Injected": "pwn"})
    with pytest.raises(ValueError, match="control"):
        StreamingComponentResponse(iter([b"<div/>"]), region_id="r", headers={"X-A\r\nY": "z"})
    from starlette.responses import Response

    decision = PreloadDecision(allowed=True, reason="ok", header_value="1", cache_control="private")
    with pytest.raises(ValueError, match="control"):
        apply_preload_headers(Response(), decision, extra={"X-A\r\nY": "z"})


def test_chart_data_urls_rejected() -> None:
    with pytest.raises(HedronError):
        reject_remote_urls({"data": {"url": "data:text/html,alert(1)"}})


def test_icon_rejects_unquoted_remote_href_and_smil_on() -> None:
    clear_icons_for_tests()
    with pytest.raises(HedronError):
        register_icon("x", "<svg><a href=https://evil.example>x</a></svg>", title="x")
    clear_icons_for_tests()
    with pytest.raises(HedronError):
        register_icon(
            "y",
            '<svg><set attributeName="onmouseover" to="alert(1)"/></svg>',
            title="y",
        )


def test_approved_headers_reject_crlf_in_values() -> None:
    with pytest.raises(ValueError, match="control"):
        approved_headers(trigger="evt\r\nHX-Redirect: https://evil.example")


def test_redirect_external_rejects_credentials() -> None:
    policy = SecurityPolicy(allow_external_redirects=True)
    with pytest.raises(HTTPException):
        redirect_external("https://user:pass@phish.example/login", policy=policy)


def test_last_event_id_with_controls_does_not_crash() -> None:
    import asyncio
    from unittest.mock import MagicMock

    backend = InMemoryJobBackend()
    handle = backend.submit("t", {}, auth_subject="alice")
    request = MagicMock()
    request.headers.get.return_value = "a\nb"
    response = job_status_sse_response(
        handle.job_id,
        backend=backend,
        request=request,
        auth_subject="alice",
        poll_interval_seconds=0.01,
    )

    async def _collect() -> bytes:
        chunks: list[bytes] = []
        async for chunk in response.body_iterator:
            chunks.append(chunk if isinstance(chunk, bytes) else bytes(chunk))
        return b"".join(chunks)

    body = asyncio.run(_collect())
    assert b"invalid-last-event-id" in body


def test_job_sse_missing_and_forbidden_http_status() -> None:
    backend = InMemoryJobBackend()
    handle = backend.submit("t", {}, auth_subject="alice")
    app = FastAPI()

    @app.get("/missing")
    def _missing():
        return job_status_sse_response("nope", backend=backend)

    @app.get("/forbidden")
    def _forbidden():
        return job_status_sse_response(handle.job_id, backend=backend, auth_subject="bob")

    with TestClient(app, raise_server_exceptions=False) as client:
        assert client.get("/missing").status_code == 404
        assert client.get("/forbidden").status_code == 403


def test_job_status_poll_requires_auth() -> None:
    backend = InMemoryJobBackend()
    handle = backend.submit("t", {}, auth_subject="alice", tenant_id="t1")
    status = backend.get(handle.job_id)
    assert status is not None
    assert job_authorized(status, auth_subject="alice", tenant_id="t1")
    with pytest.raises(HTTPException):
        job_status_response(status, auth_subject="bob", tenant_id="t1")
    response = job_status_response(status, auth_subject="alice", tenant_id="t1")
    assert response.status_code == 202


def test_job_status_poll_rejects_unscoped_jobs() -> None:
    backend = InMemoryJobBackend()
    handle = backend.submit("t", {})
    status = backend.get(handle.job_id)
    assert status is not None
    with pytest.raises(HTTPException) as exc:
        job_status_response(status, auth_subject="alice")
    assert exc.value.status_code == 403


def test_interaction_private_cache_emits_vary() -> None:
    headers = interaction_headers(InteractionResult(cache="private"))
    assert headers["Cache-Control"] == "private"
    assert "HX-Request" in headers["Vary"]
    headers2 = interaction_headers(InteractionResult(cache="no-store"))
    assert "no-store" in headers2["Cache-Control"]
    assert "HX-Request" in headers2["Vary"]


def test_sqlalchemy_rejects_projection() -> None:
    pytest.importorskip("sqlalchemy")
    from sqlalchemy import Column, Integer, String, create_engine, select
    from sqlalchemy.orm import Session, declarative_base

    from hedron_data.sqlalchemy_source import SQLAlchemyDataSource

    Base = declarative_base()

    class Item(Base):
        __tablename__ = "bugfix_round3_items"
        id = Column(Integer, primary_key=True)
        name = Column(String)

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    def factory() -> Session:
        return Session(engine)

    src = SQLAlchemyDataSource(
        session_factory=factory,
        statement=select(Item),
        to_row=lambda r: {"id": r.id, "name": r.name},
    )
    with pytest.raises(HedronError) as exc:
        src.fetch(DataQuery(projection=("name",)))
    assert exc.value.diagnostic.code == "HED-DATA-0012"
