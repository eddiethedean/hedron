"""REGRESS-058 evidence."""

from __future__ import annotations

from fastapi.testclient import TestClient

from hedron import Hedron, Text
from hedron_core.builtins.appearance import appearance_data
from hedron_core.registry import reset_registry_for_tests
from hedron_core.theme import Theme, compile_palette, default_theme


def _app() -> Hedron:
    reset_registry_for_tests()
    import hedron_core

    hedron_core._register_builtins()  # type: ignore[attr-defined]
    return Hedron(
        title="t",
        security="development",
        session_secret="test-secret",
        explorer="off",
    )


def test_page_and_command_still_work() -> None:
    app = _app()

    @app.page("/")
    def home():
        from hedron_core import Page

        return Page(Text("legacy-page"), title="Legacy")

    @app.command("/ping", fallback="/")
    def ping():
        return Text("pong")

    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert "legacy-page" in response.text
        token = response.cookies.get("hedron_csrf") or client.cookies.get("hedron_csrf") or ""
        posted = client.post(
            "/ping",
            headers={"X-CSRF-Token": token, "HX-Request": "true"},
        )
    assert posted.status_code in {200, 204, 303}


def test_theme_compile_palette_and_appearance_data() -> None:
    theme = default_theme()
    assert isinstance(theme, Theme)
    palette = compile_palette("#2563eb")
    assert "color.accent" in palette
    assert appearance_data(appearance="plain", width="field", overflow="truncate") == {
        "hedron-appearance": "plain",
        "hedron-width": "field",
        "hedron-overflow": "truncate",
    }
