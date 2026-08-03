"""FastAPI integration acceptance tests for phase 0.2."""

from __future__ import annotations

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from hedron import HTML, Hedron, HedronRouter, Page, Text, hedron_response
from hedron_core import Model, addressable, get_registry, reset_registry_for_tests
from hedron_core.registry import seal_registry


@pytest.fixture(autouse=True)
def _fresh_registry() -> None:
    reset_registry_for_tests()
    # Re-register core builtins after reset.
    import hedron_core

    hedron_core._register_builtins()  # type: ignore[attr-defined]
    yield


def test_hedron_page_and_fragment() -> None:
    app = Hedron(title="demo", security="standard", explorer="off", session_secret="test-secret")

    @app.page("/")
    def home() -> Page:
        return Page(Text("hello"), title="Demo")

    client = TestClient(app)
    page = client.get("/")
    assert page.status_code == 200
    assert page.headers["content-type"].startswith("text/html")
    assert page.text.startswith("<!DOCTYPE html>")
    assert "hello" in page.text
    assert "htmx.min.js" in page.text
    assert "X-Content-Type-Options" in page.headers

    frag = client.get("/", headers={"HX-Request": "true"})
    assert frag.status_code == 200
    assert "<!DOCTYPE" not in frag.text
    assert "hello" in frag.text


def test_plain_fastapi_html_helper() -> None:
    app = FastAPI()
    router = HedronRouter()

    @router.get("/card", **hedron_response())
    def card() -> HTML:
        return HTML(Text("plain"))

    app.state.hedron_security = __import__(
        "hedron.security.policy", fromlist=["SecurityPolicy"]
    ).SecurityPolicy.from_name("standard")
    app.include_router(router)
    client = TestClient(app)
    response = client.get("/card")
    assert response.status_code == 200
    assert "plain" in response.text


def test_json_and_html_coexist() -> None:
    class Item(Model):
        name: str

    app = Hedron(title="demo", security="standard", explorer="off", session_secret="test-secret")

    @app.get("/api/item", response_model=Item)
    def item() -> Item:
        return Item(name="x")

    @app.page("/ui")
    def ui() -> Page:
        return Page(Text("ui"), title="UI")

    client = TestClient(app)
    assert client.get("/api/item").json() == {"name": "x"}
    assert "ui" in client.get("/ui").text


def test_component_hidden_from_openapi_by_default() -> None:
    app = Hedron(title="demo", security="standard", explorer="off", session_secret="test-secret")
    router = HedronRouter(prefix="/c")

    @router.component("/box")
    def box() -> Text:
        return Text("box")

    app.include_router(router)
    client = TestClient(app)
    schema = client.get("/openapi.json").json()
    paths = schema.get("paths", {})
    assert "/c/box" not in paths or paths["/c/box"].get("get", {}).get(
        "x-hedron-kind"
    )  # may be absent
    # Default include_in_schema=False means path should be absent.
    assert "/c/box" not in paths


def test_addressable_include_component_requires_auth_deps() -> None:
    calls: list[str] = []

    def gate() -> None:
        calls.append("gate")

    @addressable
    def resource() -> Text:
        return Text("secret-resource")

    app = Hedron(title="demo", security="standard", explorer="off", session_secret="test-secret")
    router = HedronRouter(prefix="/r")
    router.include_component(resource, path="/x", dependencies=[Depends(gate)])
    app.include_router(router)
    client = TestClient(app)
    response = client.get("/r/x")
    assert response.status_code == 200
    assert "secret-resource" in response.text
    assert calls == ["gate"]


def test_csrf_required_on_action() -> None:
    app = Hedron(title="demo", security="standard", explorer="off", session_secret="test-secret")
    router = HedronRouter()

    @router.action("/do", method="POST")
    def do_action() -> Text:
        return Text("done")

    app.include_router(router)
    client = TestClient(app)
    denied = client.post("/do")
    assert denied.status_code == 403

    # Seed CSRF cookie via GET page first.
    @app.page("/seed")
    def seed() -> Page:
        return Page(Text("seed"), title="S")

    seeded = client.get("/seed")
    token = seeded.cookies.get("hedron_csrf")
    assert token
    ok = client.post("/do", headers={"X-CSRF-Token": token})
    assert ok.status_code == 200
    assert "done" in ok.text


def test_sync_and_async_endpoints() -> None:
    app = Hedron(title="demo", security="standard", explorer="off", session_secret="test-secret")

    @app.page("/sync")
    def sync_page() -> Page:
        return Page(Text("sync"), title="S")

    @app.page("/async")
    async def async_page() -> Page:
        return Page(Text("async"), title="A")

    client = TestClient(app)
    assert "sync" in client.get("/sync").text
    assert "async" in client.get("/async").text


def test_yield_dependency_cleanup() -> None:
    cleaned: list[bool] = []

    def dep():
        try:
            yield "value"
        finally:
            cleaned.append(True)

    app = Hedron(title="demo", security="standard", explorer="off", session_secret="test-secret")

    @app.page("/y")
    def page(v: str = Depends(dep)) -> Page:
        return Page(Text(v), title="Y")

    client = TestClient(app)
    assert "value" in client.get("/y").text
    assert cleaned == [True]


def test_explorer_absent_in_production_profile() -> None:
    app = Hedron(title="demo", security="standard", explorer="off", session_secret="test-secret")
    client = TestClient(app)
    assert client.get("/hedron-explorer/").status_code == 404


def test_explorer_present_in_development() -> None:
    app = Hedron(
        title="demo", security="development", explorer="development", session_secret="test-secret"
    )
    client = TestClient(app)
    response = client.get("/hedron-explorer/")
    assert response.status_code == 200
    assert "Hedron Explorer" in response.text


def test_registry_routes_visible_to_cli_surface() -> None:
    app = Hedron(title="demo", security="standard", explorer="off", session_secret="test-secret")

    @app.page("/cli-page")
    def cli_page() -> Page:
        return Page(Text("cli"), title="C")

    seal_registry()
    routes = list(get_registry().routes())
    assert any(r.name == "cli_page" for r in routes)
