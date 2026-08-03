"""Additional FastAPI MVP defect-regression tests."""

from __future__ import annotations

import base64
import hashlib

import pytest
from fastapi import FastAPI, Form, Request
from fastapi.testclient import TestClient

from hedron import (
    HTML,
    Hedron,
    HedronRouter,
    Page,
    Pagination,
    Text,
    approved_headers,
    hedron_response,
    htmx_context,
    mount_hedron_static,
    redirect_external,
    render,
)
from hedron.security.policy import SecurityPolicy
from hedron_core import reset_registry_for_tests


@pytest.fixture(autouse=True)
def _fresh_registry() -> None:
    reset_registry_for_tests()
    import hedron_core

    hedron_core._register_builtins()  # type: ignore[attr-defined]
    yield


def test_plain_fastapi_html_helper_hits_html_route() -> None:
    app = FastAPI()
    router = HedronRouter()

    @router.get("/card", **hedron_response())
    def card() -> HTML:
        return HTML(Text("plain-card"))

    app.state.hedron_security = SecurityPolicy.from_name("standard")
    app.include_router(router)
    client = TestClient(app)
    response = client.get("/card")
    assert response.status_code == 200
    assert "plain-card" in response.text


def test_csrf_cookie_reused_and_form_token_accepted() -> None:
    app = Hedron(title="demo", security="standard", explorer="off", session_secret="test-secret")
    router = HedronRouter()

    @router.page("/seed")
    def seed() -> Page:
        return Page(Text("seed"), title="S")

    @router.action("/do", method="POST")
    def do_action(note: str = Form("ok")) -> Text:
        return Text(note)

    app.include_router(router)
    client = TestClient(app)
    first = client.get("/seed")
    token = first.cookies.get("hedron_csrf")
    assert token
    second = client.get("/seed")
    assert second.cookies.get("hedron_csrf") in {None, token}
    # Cookie jar still has the original token.
    assert client.cookies.get("hedron_csrf") == token

    denied = client.post("/do", data={"note": "x", "csrf_token": "forged"})
    assert denied.status_code == 403

    ok = client.post("/do", data={"note": "done", "csrf_token": token})
    assert ok.status_code == 200
    assert "done" in ok.text


def test_redirect_external_respects_policy() -> None:
    from fastapi import HTTPException

    policy = SecurityPolicy.from_name("standard")
    assert policy.allow_external_redirects is False
    with pytest.raises(HTTPException):
        redirect_external("https://evil.example/phish", policy=policy)
    allowed = SecurityPolicy(allow_external_redirects=True)
    response = redirect_external("https://example.com/ok", policy=allowed)
    assert response.status_code == 303
    with pytest.raises(HTTPException):
        redirect_external("javascript:alert(1)", policy=allowed)


def test_approved_headers_reject_external_push_and_location() -> None:
    with pytest.raises(ValueError):
        approved_headers(push_url="https://evil.example")
    with pytest.raises(ValueError):
        approved_headers(location="https://evil.example")
    headers = approved_headers(push_url="/local", location="/elsewhere")
    assert headers["HX-Push-Url"] == "/local"
    assert headers["HX-Location"] == "/elsewhere"


def test_approved_headers_cover_htmx_2_response_surface() -> None:
    headers = approved_headers(
        trigger_after_swap={"usersChanged": {"count": 2}},
        trigger_after_settle="usersSettled",
        replace_url="/users?page=2",
        reselect="#user-table",
    )
    assert headers["HX-Trigger-After-Swap"] == '{"usersChanged": {"count": 2}}'
    assert headers["HX-Trigger-After-Settle"] == "usersSettled"
    assert headers["HX-Replace-Url"] == "/users?page=2"
    assert headers["HX-Reselect"] == "#user-table"

    with pytest.raises(ValueError):
        approved_headers(replace_url="https://evil.example")
    with pytest.raises(ValueError):
        approved_headers(reselect="body; script")


def test_htmx_context_exposes_official_request_headers() -> None:
    app = FastAPI()

    @app.get("/")
    def context(request: Request) -> dict[str, object]:
        ctx = htmx_context(request)
        return {
            "is_htmx": ctx.is_htmx,
            "trigger_name": ctx.trigger_name,
            "prompt": ctx.prompt,
            "boosted": ctx.boosted,
            "history_restore": ctx.history_restore,
        }

    response = TestClient(app).get(
        "/",
        headers={
            "HX-Request": "true",
            "HX-Trigger-Name": "save",
            "HX-Prompt": "confirmed",
            "HX-Boosted": "true",
        },
    )
    assert response.json() == {
        "is_htmx": True,
        "trigger_name": "save",
        "prompt": "confirmed",
        "boosted": True,
        "history_restore": False,
    }

    history = TestClient(app).get("/", headers={"HX-History-Restore-Request": "true"})
    assert history.json() == {
        "is_htmx": False,
        "trigger_name": None,
        "prompt": None,
        "boosted": False,
        "history_restore": True,
    }


def test_history_restore_uses_page_mode() -> None:
    app = Hedron(title="demo", security="standard", explorer="off", session_secret="test-secret")

    @app.page("/")
    def home() -> Page:
        return Page(Text("home"), title="Home")

    client = TestClient(app)
    response = client.get(
        "/",
        headers={"HX-Request": "true", "HX-History-Restore-Request": "true"},
    )
    assert response.status_code == 200
    assert response.text.startswith("<!DOCTYPE html>")
    assert 'name="htmx-config"' in response.text
    assert '"historyRestoreAsHxRequest":false' in response.text
    assert '"allowEval":false' in response.text


def test_explicit_htmx_config_replaces_hedron_defaults() -> None:
    from hedron import html

    app = Hedron(title="demo", security="standard", explorer="off", session_secret="test-secret")

    @app.page("/")
    def home() -> Page:
        return Page(
            Text("home"),
            title="Home",
            head=html.meta(name="htmx-config", content='{"allowEval":true}'),
        )

    response = TestClient(app).get("/")
    assert response.text.count('name="htmx-config"') == 1
    assert 'content="{&quot;allowEval&quot;:true}"' in response.text
    assert '"historyRestoreAsHxRequest":false' not in response.text


def test_pagination_renders_with_safe_urls() -> None:
    html = render(
        Pagination(page=1, page_size=10, total=25, base_path="/items", target="#list")
    ).html
    assert "hedron-pagination" in html
    assert 'href="/items?page=1"' in html
    assert 'hx-get="/items?page=2"' in html


def test_htmx_static_mounted_for_plain_and_hedron() -> None:
    hedron = Hedron(title="demo", security="standard", explorer="off", session_secret="test-secret")
    plain = FastAPI()
    mount_hedron_static(plain)
    for app in (hedron, plain):
        client = TestClient(app)
        asset = client.get("/hedron-static/htmx.min.js")
        assert asset.status_code == 200
        assert len(asset.content) > 1000
        digest = base64.b64encode(hashlib.sha384(asset.content).digest()).decode("ascii")
        assert digest == "H5SrcfygHmAuTDZphMHqBJLc3FhssKjG7w/CeCpFReSfwBWDTKpkzPP8c+cLsK+V"


def test_authenticated_cache_headers() -> None:
    app = Hedron(title="demo", security="standard", explorer="off", session_secret="test-secret")

    @app.page("/")
    def home(request: Request) -> Page:
        request.state.hedron_authenticated = True
        return Page(Text("private"), title="P")

    client = TestClient(app)
    response = client.get("/")
    assert response.headers.get("Cache-Control") == "private, no-store"


def test_explorer_development_mounts_under_standard() -> None:
    app = Hedron(
        title="demo",
        security="standard",
        explorer="development",
        session_secret="test-secret",
    )
    client = TestClient(app)
    response = client.get("/hedron-explorer/")
    assert response.status_code == 200
    assert "Hedron Explorer" in response.text


def test_explorer_secured_requires_auth() -> None:
    app = Hedron(
        title="demo",
        security="standard",
        explorer="secured",
        session_secret="test-secret",
    )
    client = TestClient(app)
    denied = client.get("/hedron-explorer/")
    assert denied.status_code == 401
