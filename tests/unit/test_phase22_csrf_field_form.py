"""Phase 0.22 CsrfField + Form HTMX kwargs (FORM-022)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from starlette.requests import Request

from hedron import CsrfField, Form, Hedron, Hx, Page, Text, csrf_token_for_request
from hedron_core.rendering import RenderContext, RenderMode, render


def test_csrf_field_with_explicit_token() -> None:
    html = render(CsrfField(token="abc", name="csrf_token"), mode=RenderMode.FRAGMENT).html
    assert 'type="hidden"' in html
    assert 'name="csrf_token"' in html
    assert 'value="abc"' in html


def test_csrf_field_reads_render_context() -> None:
    ctx = RenderContext.standalone(csrf_token="from-ctx", csrf_form_field="csrf_token")
    html = render(CsrfField(), context=ctx, mode=RenderMode.FRAGMENT).html
    assert 'value="from-ctx"' in html


def test_csrf_field_requires_token_without_context() -> None:
    try:
        render(CsrfField(), mode=RenderMode.FRAGMENT)
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "CsrfField requires token" in str(exc)


def test_form_hx_emits_validated_attrs() -> None:
    node = Form(
        Text("body"),
        action="/save",
        method="post",
        hx=Hx(target="#region", swap="outerHTML", indicator="#busy"),
    )
    html = render(node, mode=RenderMode.FRAGMENT).html
    assert 'hx-target="#region"' in html
    assert 'hx-swap="outerHTML"' in html
    assert 'hx-indicator="#busy"' in html
    assert 'method="post"' in html


def test_form_hx_rejects_unsafe_selector() -> None:
    try:
        Form(Text("x"), hx=Hx(target="javascript:alert(1)"))
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "Unsafe HTMX" in str(exc)


def test_form_kwargs_cannot_bypass_hx_validation() -> None:
    try:
        Form(Text("x"), **{"hx-target": "javascript:alert(1)"})
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "Unsafe HTMX" in str(exc)


def test_form_hx_wins_over_unsafe_kwargs() -> None:
    node = Form(
        Text("x"),
        hx=Hx(target="#ok"),
        **{"hx-target": "javascript:alert(1)"},
    )
    html = render(node, mode=RenderMode.FRAGMENT).html
    assert 'hx-target="#ok"' in html
    assert "javascript:" not in html


def test_fastapi_form_csrf_field_roundtrip() -> None:
    app = Hedron(title="form-022", security="standard", explorer="off", session_secret="test")

    @app.page("/")
    def home(request: Request) -> Page:
        token = csrf_token_for_request(request, request.app.state.hedron_security)
        return Page(
            Form(
                CsrfField(token=token),
                Text("form"),
                action="/save",
                method="post",
                hx=Hx(target="#main", swap="outerHTML"),
            ),
            title="home",
        )

    @app.action("/save")
    def save() -> Page:
        return Page(Text("saved"), title="saved")

    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert 'name="csrf_token"' in response.text
    assert 'hx-target="#main"' in response.text
    cookie = response.cookies.get("hedron_csrf")
    assert cookie
    denied = client.post("/save")
    assert denied.status_code == 403
    ok = client.post("/save", headers={"X-CSRF-Token": cookie})
    assert ok.status_code == 200
    assert "saved" in ok.text


def test_standard_csrf_secure_with_forwarded_proto(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from starlette.responses import Response

    from hedron.security.csrf import ensure_csrf_cookie
    from hedron.security.policy import SecurityPolicy

    monkeypatch.setenv("HEDRON_TRUSTED_PROXIES", "127.0.0.1")
    policy = SecurityPolicy.from_name("standard")
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [(b"x-forwarded-proto", b"https")],
        "scheme": "http",
        "server": ("testserver", 80),
        "client": ("127.0.0.1", 123),
    }
    request = Request(scope)
    response = Response("ok")
    ensure_csrf_cookie(response, policy, token="abc", request=request)
    assert "Secure" in (response.headers.get("set-cookie") or "")


def test_standard_csrf_ignores_untrusted_forwarded_proto(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from starlette.responses import Response

    from hedron.security.csrf import ensure_csrf_cookie
    from hedron.security.policy import SecurityPolicy

    monkeypatch.delenv("HEDRON_TRUSTED_PROXIES", raising=False)
    policy = SecurityPolicy.from_name("standard")
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [(b"x-forwarded-proto", b"https")],
        "scheme": "http",
        "server": ("testserver", 80),
        "client": ("10.0.0.9", 123),
    }
    request = Request(scope)
    response = Response("ok")
    ensure_csrf_cookie(response, policy, token="abc", request=request)
    assert "Secure" not in (response.headers.get("set-cookie") or "")
