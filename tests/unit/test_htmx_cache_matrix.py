"""Cache separation and interaction-status matrix (phase 0.8)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from hedron import Hedron, InteractionResult, Page, Text
from hedron.interaction import FragmentRegion, InteractionPolicy


def _app() -> Hedron:
    app = Hedron(
        title="CacheMatrix",
        security="standard",
        session_secret="test-secret",
        explorer="off",
    )
    regions = (FragmentRegion(id="main", selector="#main"),)

    @app.page("/", fragment_regions=regions)
    def home() -> Page:
        return Page(Text("home"), title="Home")

    @app.component("/frag", fragment_regions=regions)
    def frag() -> InteractionResult:
        return InteractionResult(
            content=Text("fragment"),
            policy=InteractionPolicy(declared_regions=regions, vary_on_target=True),
            cache="vary-htmx",
        )

    @app.component("/accepted")
    def accepted() -> InteractionResult:
        return InteractionResult(content=Text("ok"), status_code=202, explanation="accepted")

    return app


def test_page_vs_fragment_vary() -> None:
    client = TestClient(_app())
    page = client.get("/")
    frag = client.get("/frag", headers={"HX-Request": "true", "HX-Target": "#main"})
    assert page.status_code == 200
    assert frag.status_code == 200
    assert "<html" in page.text.lower()
    assert "<html" not in frag.text.lower()
    assert "HX-Request" in frag.headers.get("vary", "")


def test_unauthorized_target_forbidden() -> None:
    client = TestClient(_app())
    response = client.get("/frag", headers={"HX-Request": "true", "HX-Target": "#evil"})
    assert response.status_code == 403


def test_non_htmx_fallback_still_html() -> None:
    client = TestClient(_app())
    response = client.get("/frag")
    assert response.status_code == 200
    assert "fragment" in response.text


def test_accepted_status_preserved() -> None:
    client = TestClient(_app())
    response = client.get("/accepted", headers={"HX-Request": "true"})
    assert response.status_code == 202
