"""ELEMENT-046: opt-in schema-aware elements; native remains canonical."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field
from tests.unit._helpers_046 import make_app, reset_046

from hedron import Control, FormBody, Text
from hedron_core.rendering import render
from hedron_elements.schema import CONTROL_ELEMENT_MAP, element_tag_for_kind


def setup_function() -> None:
    reset_046()


def test_native_form_remains_canonical() -> None:
    app = make_app()

    class NoteIn(BaseModel):
        title: Annotated[str, Field(min_length=1), Control(kind="text", label="Title")]
        kind: Literal["a", "b"] = "a"

    @app.command(fallback="/")
    def add(data: Annotated[NoteIn, FormBody()]):
        return Text(data.title)

    html = render(add.form()).html
    assert "<form" in html
    assert "<hedron-field-text" not in html
    assert CONTROL_ELEMENT_MAP["text"] == "hedron-field-text"
    assert element_tag_for_kind("file") == "hedron-field-file"


def test_opt_in_elements_wrap_native_controls() -> None:
    app = make_app()

    class NoteIn(BaseModel):
        title: Annotated[str, Control(kind="text")]
        kind: Literal["a", "b"] = "a"

    @app.command(fallback="/")
    def add(data: Annotated[NoteIn, FormBody()]):
        return Text(data.title)

    html = render(add.form(enhance="elements")).html
    assert "<form" in html
    assert "hedron-field-text" in html
    assert "<input" in html
