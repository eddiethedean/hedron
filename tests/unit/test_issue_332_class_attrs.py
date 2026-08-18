"""#332: RefreshableView.empty/cache and CommandHandler.effects must apply."""

from __future__ import annotations

from fastapi.testclient import TestClient
from tests.unit._helpers_044 import make_app, reset_044

from hedron import CommandHandler, Page, RefreshableView, Refreshes, Text, refresh
from hedron_core.codes import HED_TYPE_0006
from hedron_core.diagnostics import HedronError


def setup_function() -> None:
    reset_044()


def test_class_empty_and_cache_apply() -> None:
    app = make_app()

    class EmptyView(RefreshableView[None, str]):
        empty = Text("none")
        cache = "no-store"

        def load(self) -> str:
            return ""

        def render(self, data: str):
            return Text(data or "rendered")

    handle = app.refreshable(EmptyView)

    @app.page("/")
    def home():
        return Page(handle(), title="Home")

    client = TestClient(app)
    page = client.get("/")
    assert page.status_code == 200
    response = client.get(
        handle.path,
        headers={"HX-Request": "true", "HX-Target": handle.dom_id},
    )
    assert response.status_code == 200
    assert "none" in response.text
    assert "no-store" in (response.headers.get("Cache-Control") or "")


def test_class_effects_are_declared() -> None:
    app = make_app()

    @app.refreshable
    def notes():
        return Text("notes")

    class Add(CommandHandler[None, object]):
        fallback = "/"
        effects = Refreshes(notes)

        def execute(self):
            return refresh(notes)

    handle = app.command(Add)
    assert handle.descriptor.effect == "declared"
    assert notes.logical_id in (handle.schema.declared_target_ids or ())  # type: ignore[union-attr]


def test_class_undeclared_refresh_fails() -> None:
    app = make_app()

    @app.refreshable
    def notes():
        return Text("notes")

    @app.refreshable
    def other():
        return Text("other")

    class Add(CommandHandler[None, object]):
        fallback = "/"
        effects = Refreshes(notes)

        def execute(self):
            return refresh(other)

    handle = app.command(Add)

    @app.page("/")
    def home():
        return Page(notes(), title="Home")

    client = TestClient(app)
    token = client.get("/").cookies.get("hedron_csrf") or ""
    try:
        response = client.post(handle.path, headers={"HX-Request": "true", "X-CSRF-Token": token})
    except HedronError as caught:
        assert caught.diagnostics[0].code == HED_TYPE_0006
        return
    assert response.status_code >= 400
