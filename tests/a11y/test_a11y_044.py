"""A11Y-044: generated form labels, errors, no custom elements."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field
from tests.unit._helpers_044 import make_app, reset_044

from hedron import Control, FormBody, Text
from hedron_core.rendering import render


def setup_function() -> None:
    reset_044()


class NoteIn(BaseModel):
    title: Annotated[str, Field(min_length=1), Control(label="Title")]
    body: Annotated[str, Control(kind="textarea")]


def test_generated_form_has_labels_and_no_custom_element() -> None:
    app = make_app()

    @app.command(fallback="/")
    def add(data: Annotated[NoteIn, FormBody()]):
        return Text(data.title)

    html = render(add.form()).html
    assert "<label" in html
    assert "<form" in html
    assert "<button" in html
    assert "<hedron-" not in html
    assert "custom-element" not in html


def test_error_summary_role_alert() -> None:
    app = make_app()

    @app.command(fallback="/")
    def add(data: Annotated[NoteIn, FormBody()]):
        return Text(data.title)

    html = render(add.form(errors=[{"loc": ("title",), "msg": "Required"}])).html
    assert "Required" in html
    assert 'role="alert"' in html
