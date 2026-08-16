"""A11Y-045: native form / no custom elements remain; Explorer tables are keyboard-reachable."""

from __future__ import annotations

from typing import Annotated

from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from tests.unit._helpers_045 import make_app, reset_045

from hedron import Control, FormBody, Page, Text
from hedron_core.rendering import render


def setup_function() -> None:
    reset_045()


def test_generated_form_remains_native_and_no_js_required() -> None:
    app = make_app()

    class NoteIn(BaseModel):
        title: Annotated[str, Field(min_length=1), Control(label="Title")]

    @app.command(fallback="/")
    def add(data: Annotated[NoteIn, FormBody()]):
        return Text(data.title)

    html = render(add.form()).html
    assert "<form" in html
    assert "<label" in html
    assert "<hedron-" not in html
    assert "custom-element" not in html
    assert "javascript:" not in html.lower()


def test_explorer_catalog_table_has_keyboard_landmarks() -> None:
    app = make_app(explorer="development")

    @app.refreshable
    def status():
        return Text("ok")

    @app.page("/")
    def home():
        return Page(status(), title="Home")

    html = TestClient(app).get("/hedron-explorer/interactions").text
    assert 'href="#main"' in html or 'id="main"' in html
    assert "<table" in html
    assert "Skip to content" in html
    assert "SR-021" not in html
    assert "Supported human AT" not in html
