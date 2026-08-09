"""Phase 0.6 interaction, charts, and content coverage."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from hedron import Hedron, InteractionResult, Text
from hedron.interaction import (
    FragmentRegion,
    InteractionPolicy,
    OobUpdate,
    htmx_request,
    interaction_headers,
)
from hedron_core.rendering import RenderMode, render
from hedron_core.security import TrustedHtml


def test_interaction_result_headers_include_vary() -> None:
    result = InteractionResult(
        content=Text("ok"),
        cache="vary-htmx",
        policy=InteractionPolicy(
            declared_regions=(FragmentRegion(id="main", selector="#main"),),
            vary_on_target=True,
        ),
    )
    headers = interaction_headers(result)
    assert "HX-Request" in headers.get("Vary", "")
    assert "HX-History-Restore-Request" in headers["Vary"]
    assert "HX-Target" in headers["Vary"]


def test_htmx_validation_returns_html_fragment() -> None:
    app = Hedron(title="t", security="standard", session_secret="test-secret", explorer="off")

    @app.action("/validate", method="POST")
    def validate(amount: int) -> InteractionResult:  # noqa: ARG001
        return InteractionResult(content=Text("ok"))

    client = TestClient(app)
    response = client.post(
        "/validate",
        data={"amount": "not-int"},
        headers={"HX-Request": "true", "HX-Target": "#main"},
    )
    assert response.status_code == 422
    assert "text/html" in response.headers["content-type"]
    assert "hedron-validation-errors" in response.text


def test_htmx_validation_json_for_non_htmx() -> None:
    app = Hedron(title="t", security="standard", session_secret="test-secret", explorer="off")

    @app.action("/validate2", method="POST")
    def validate2(amount: int) -> dict[str, int]:
        return {"amount": amount}

    client = TestClient(app)

    # CSRF may block; disable by using GET page first... use standard and get cookie
    # For non-HTMX JSON path, CSRF still applies on POST — seed cookie via GET /
    @app.page("/")
    def home() -> Text:
        return Text("home")

    client.get("/")
    response = client.post("/validate2", data={"amount": "x"})
    assert response.status_code == 422
    assert "application/json" in response.headers["content-type"]


def test_line_chart_renders_accessible_markup() -> None:
    from hedron_charts import LineChart

    node = LineChart(
        [{"month": "Jan", "revenue": 1}, {"month": "Feb", "revenue": 2}],
        x="month",
        y="revenue",
        title="Revenue",
        description="Up and to the right",
    )
    html = render(node, mode=RenderMode.FRAGMENT).html
    assert "Revenue" in html
    assert "Up and to the right" in html


def test_matplotlib_chart_when_available() -> None:
    pytest.importorskip("matplotlib")
    import matplotlib.pyplot as plt

    from hedron_charts import MatplotlibChart

    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
    node = MatplotlibChart(fig, title="Squares", description="y = x^2", alt="Quadratic")
    html = render(node, mode=RenderMode.FRAGMENT).html
    plt.close(fig)
    assert "Squares" in html
    assert "<svg" in html.lower() or "image/svg" in html.lower() or "figure" in html.lower()


def test_trusted_html_nh3() -> None:
    pytest.importorskip("nh3")
    trusted = TrustedHtml.nh3("<b>ok</b><script>alert(1)</script>")
    assert "<script" not in trusted.value.lower()
    assert "ok" in trusted.value
    assert trusted.source.startswith("nh3:")


def test_markdown_component() -> None:
    pytest.importorskip("markdown")
    pytest.importorskip("nh3")
    from hedron.content import Markdown

    html = render(Markdown("# Hello"), mode=RenderMode.FRAGMENT).html
    assert "Hello" in html
    assert "hedron-markdown" in html


def test_icon_registry() -> None:
    from hedron_core.icons import clear_icons_for_tests, get_icon, register_icon

    clear_icons_for_tests()
    register_icon("check", '<svg xmlns="http://www.w3.org/2000/svg"></svg>', title="Check")
    assert get_icon("check").title == "Check"


def test_interaction_result_endpoint() -> None:
    app = Hedron(title="t", security="standard", session_secret="test-secret", explorer="off")

    @app.component("/frag")
    def frag() -> InteractionResult:
        return InteractionResult(
            content=Text("primary"),
            oob=(OobUpdate(content=Text("side"), element_id="hedron-toast"),),
            trigger={"done": True},
        )

    client = TestClient(app)
    response = client.get("/frag", headers={"HX-Request": "true"})
    assert response.status_code == 200
    assert "primary" in response.text
    assert "HX-Trigger" in response.headers
    assert "Vary" in response.headers


def test_aggrid_asset_registration() -> None:
    from hedron_core.registry import get_registry, reset_registry_for_tests
    from hedron_data.aggrid import ensure_aggrid_assets

    reset_registry_for_tests()
    meta = ensure_aggrid_assets()
    assert meta["backend"] == "aggrid-community"
    assets = {a.logical_id for a in get_registry().assets()}
    assert "hedron-data:aggrid.host.js" in assets


def test_require_sqlalchemy_ok_when_installed() -> None:
    pytest.importorskip("sqlalchemy")
    from hedron_data.sqlalchemy_source import require_sqlalchemy

    module = require_sqlalchemy()
    assert module.__name__ == "sqlalchemy"


def test_require_sqlalchemy_raises_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    import builtins

    from hedron_core.diagnostics import HedronError
    from hedron_data.sqlalchemy_source import require_sqlalchemy

    real_import = builtins.__import__

    def _no_sqlalchemy(name: str, *args: object, **kwargs: object):  # noqa: ANN001
        if name == "sqlalchemy" or name.startswith("sqlalchemy."):
            raise ImportError("forced")
        return real_import(name, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(builtins, "__import__", _no_sqlalchemy)
    with pytest.raises(HedronError) as exc:
        require_sqlalchemy()
    assert exc.value.diagnostic.code == "HED-DATA-0010"


def test_cache_hints_and_explorer_trace() -> None:
    from starlette.requests import Request

    from hedron.interaction import interaction_headers

    private = interaction_headers(InteractionResult(content=Text("x"), cache="private"))
    assert private["Cache-Control"] == "private"
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "path": "/",
        "raw_path": b"/",
        "root_path": "",
        "scheme": "http",
        "server": ("test", 80),
        "client": ("test", 123),
        "headers": [(b"hx-request", b"true")],
    }
    request = Request(scope)
    interaction_headers(
        InteractionResult(content=Text("x"), cache="no-store", explanation="cached"),
        request=request,
    )
    assert request.state.hedron_interaction["cache"] == "no-store"


def test_htmx_request_wrapper() -> None:
    from starlette.requests import Request

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/ctx",
        "raw_path": b"/ctx",
        "query_string": b"",
        "headers": [
            (b"hx-request", b"true"),
            (b"hx-target", b"#main"),
        ],
        "client": ("test", 50000),
        "server": ("test", 80),
    }
    request = Request(scope)
    hx = htmx_request(request)
    assert hx.is_htmx is True
    assert hx.target == "#main"
