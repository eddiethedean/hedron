"""SCREEN-058 evidence."""

from __future__ import annotations

from fastapi.testclient import TestClient

from hedron import Hedron, ScreenHandle, Text
from hedron_core.registry import reset_registry_for_tests


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


def test_screen_registers_route_and_metadata() -> None:
    app = _app()

    @app.screen("/", title="Home", name="home", layout="stack")
    def home():
        return Text("welcome-home")

    assert isinstance(home, ScreenHandle)
    assert home.path == "/"
    assert home.name == "home"
    assert home.title == "Home"
    assert home.layout == "stack"
    assert home.logical_id == "screen:home"
    assert app.state.hedron_handles["screen:home"] is home


def test_screen_get_returns_title_content() -> None:
    app = _app()

    @app.screen("/", title="Home Screen")
    def home():
        return Text("welcome-home")

    with TestClient(app) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert "Home Screen" in response.text
    assert "welcome-home" in response.text
