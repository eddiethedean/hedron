"""FORM-058 evidence."""

from __future__ import annotations

from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from hedron import Hedron, Text
from hedron_core.registry import reset_registry_for_tests
from hedron_core.rendering import RenderContext, RenderMode, render


class Note(BaseModel):
    message: str = Field(min_length=1, max_length=200)


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


def test_form_command_renders_and_posts() -> None:
    app = _app()

    @app.form_command("/notes", fallback="/", success="Saved")
    def add_note(data: Note):
        return Text(data.message)

    @app.screen("/", title="Home")
    def home():
        return add_note.form(submit_label="Save")

    form_html = render(
        add_note.form(submit_label="Save"),
        context=RenderContext.standalone(),
        mode=RenderMode.FRAGMENT,
    ).html
    assert "message" in form_html.lower() or "Save" in form_html

    with TestClient(app) as client:
        home = client.get("/")
        assert home.status_code == 200
        token = home.cookies.get("hedron_csrf") or client.cookies.get("hedron_csrf") or ""
        response = client.post(
            "/notes",
            data={"message": "hello-form"},
            headers={"X-CSRF-Token": token, "HX-Request": "true"},
        )
    assert response.status_code in {200, 204, 303}
    if response.status_code == 200:
        assert "hello-form" in response.text or "Saved" in response.text
