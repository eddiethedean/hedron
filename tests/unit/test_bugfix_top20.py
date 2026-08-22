"""Regression tests for the top-20 severity bug-fix pass."""

from __future__ import annotations

import pytest
from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from starlette.testclient import TestClient

from hedron.builtins.chat import ChatInput
from hedron.security.csrf import ensure_csrf_cookie
from hedron.security.headers import SecurityHeadersMiddleware
from hedron.security.policy import SecurityPolicy
from hedron.security.redirects import redirect_local
from hedron.state import SessionState
from hedron_core import Text, render
from hedron_core.diagnostics import HedronError
from hedron_core.auto import Auto
from hedron_core.html import html
from hedron_core.live import SseEvent, encode_sse
from hedron_core.models import Model
from hedron_core.security import SafeUrl, Secret, UrlPurpose
from hedron_core.streaming import ChunkedList
from hedron_data.columns import columns_from_model
from hedron_data.memory import InMemoryDataSource
from hedron_data.sources import CellUpdate, DataChanges, DataQuery


def test_encode_sse_rejects_injected_id_and_event() -> None:
    with pytest.raises(ValueError, match="SSE id"):
        encode_sse(SseEvent(data="x", id="a\nevent: pwned"))
    with pytest.raises(ValueError, match="SSE event"):
        encode_sse(SseEvent(data="x", event="msg\ndata: injected"))


def test_redirect_local_rejects_encoded_open_redirects() -> None:
    for bad in (
        "/%2f%2fevil.example",
        "/%2F%2Fevil.example",
        "/foo/%2e%2e/%2e%2e/evil",
        "/..%2f..%2fevil",
    ):
        with pytest.raises(HTTPException):
            redirect_local(bad)


def test_safe_url_allows_colon_in_path() -> None:
    url = SafeUrl.parse("/api/data:export", purpose=UrlPurpose.NAVIGATION)
    assert url.value == "/api/data:export"


def test_safe_url_rejects_malformed_external_hosts_and_ports() -> None:
    for raw in ("https://example.com:abc/x", "https://example.com:99999/x", "https://[::1/x"):
        with pytest.raises(HedronError):
            SafeUrl.parse(raw, purpose=UrlPurpose.NAVIGATION, allow_external=True)


def test_hx_push_url_bool_serializes() -> None:
    node = html.div("x", **{"hx-push-url": True})
    out = render(node).html
    assert 'hx-push-url="true"' in out
    node2 = html.div("x", **{"hx-replace-url": "false"})
    out2 = render(node2).html
    assert 'hx-replace-url="false"' in out2


def test_stream_fallback_escapes_region_id() -> None:
    chunked = ChunkedList(
        items=[],
        region_id='"><img src=x onerror=alert(1)>',
        item_html=lambda _item, _i: "",
    )
    fb = chunked.fallback()
    assert "<img" not in fb
    assert "&quot;" in fb or "&#x27;" in fb or "&gt;" in fb


def test_session_state_without_session_middleware() -> None:
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 123),
        "server": ("test", 80),
    }
    request = Request(scope)
    state = SessionState(request, "k", str)
    assert state.value is None
    with pytest.raises(RuntimeError, match="SessionMiddleware"):
        state.value = "ok"
    with pytest.raises(RuntimeError, match="SessionMiddleware"):
        state.clear()


def test_strict_csrf_cookie_always_secure() -> None:
    policy = SecurityPolicy.from_name("strict")
    response = Response()
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 123),
        "server": ("test", 80),
    }
    request = Request(scope)
    ensure_csrf_cookie(response, policy, token="tok", request=request)
    set_cookie = response.headers.get("set-cookie", "")
    assert "Secure" in set_cookie


def test_secret_annotation_marks_column_secret_and_readonly() -> None:
    class Row(Model):
        id: str
        token: Secret[str]
        name: str

    cols = {c.name: c for c in columns_from_model(Row)}
    assert cols["token"].secret is True
    assert cols["token"].read_only is True
    assert cols["name"].secret is False


def test_inmemory_apply_is_transactional() -> None:
    src = InMemoryDataSource(
        [{"id": "1", "name": "Ada"}, {"id": "2", "name": "Bob"}],
        writable_fields=frozenset({"name"}),
    )
    before = src.fetch(DataQuery()).rows
    result = src.apply(
        DataChanges(
            updates=(
                CellUpdate(row_key="1", field="name", value="Ada2"),
                CellUpdate(row_key="missing", field="name", value="X"),
            )
        )
    )
    assert result.ok is False
    after = src.fetch(DataQuery()).rows
    assert after == before


def test_chat_input_emits_csrf() -> None:
    html_out = render(ChatInput(action="/send", csrf_token="abc123")).html
    assert 'name="csrf_token"' in html_out
    assert "abc123" in html_out
    assert "X-CSRF-Token" in html_out


def test_auto_render_preserves_component_identity() -> None:
    from hedron_core.diagnostics import HedronError

    with pytest.raises(HedronError) as exc:
        render([Auto(Text("a").key("same")), Auto(Text("b").key("same"))])
    assert exc.value.diagnostic.code == "HED-RENDER-0013"


def test_authenticated_cache_control_overrides_public() -> None:
    from starlette.applications import Starlette
    from starlette.responses import PlainTextResponse
    from starlette.routing import Route

    async def homepage(request: Request) -> Response:
        request.state.hedron_authenticated = True
        return PlainTextResponse("ok", headers={"Cache-Control": "public, max-age=60"})

    app = Starlette(routes=[Route("/", homepage)])
    app.add_middleware(
        SecurityHeadersMiddleware,
        policy=SecurityPolicy.from_name("standard"),
    )
    with TestClient(app) as client:
        response = client.get("/")
    assert response.headers["cache-control"] == "private, no-store"


def test_reject_active_svg_blocks_iframe_srcdoc() -> None:
    from hedron_charts.limits import reject_active_svg
    from hedron_core.diagnostics import HedronError

    payload = '"><iframe srcdoc="&lt;img src=x o&#110;error=alert(1)&gt;">'
    with pytest.raises(HedronError) as exc:
        reject_active_svg(f'<svg aria-label="{payload}"></svg>')
    assert exc.value.diagnostic.code == "HED-CHART-0006"


def test_line_chart_fallback_escapes_title(monkeypatch: pytest.MonkeyPatch) -> None:
    import builtins

    from hedron_charts.components import LineChart

    real_import = builtins.__import__

    def _no_matplotlib(name: str, *args: object, **kwargs: object):
        if name == "matplotlib" or name.startswith("matplotlib."):
            raise ImportError("forced")
        return real_import(name, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(builtins, "__import__", _no_matplotlib)
    node = LineChart(
        [{"x": 1, "y": 2}, {"x": 2, "y": 3}],
        x="x",
        y="y",
        title='"><iframe srcdoc="x">',
        description="Line chart fallback escape regression",
        alt="chart",
    )
    out = render(node).html
    assert "<iframe" not in out
    assert "&quot;" in out or "&gt;" in out


def test_sqlalchemy_rejects_filters() -> None:
    pytest.importorskip("sqlalchemy")
    from sqlalchemy import Column, Integer, String, create_engine, select
    from sqlalchemy.orm import Session, declarative_base

    from hedron_core.diagnostics import HedronError
    from hedron_data.sqlalchemy_source import SQLAlchemyDataSource

    Base = declarative_base()

    class Item(Base):
        __tablename__ = "bugfix_items"
        id = Column(Integer, primary_key=True)
        name = Column(String)

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(Item(id=1, name="a"))
        session.commit()

    def factory() -> Session:
        return Session(engine)

    src = SQLAlchemyDataSource(
        session_factory=factory,
        statement=select(Item),
        to_row=lambda r: {"id": r.id, "name": r.name},
    )
    with pytest.raises(HedronError) as exc:
        src.fetch(DataQuery(filters={"name": "a"}))
    assert exc.value.diagnostic.code == "HED-DATA-0012"
