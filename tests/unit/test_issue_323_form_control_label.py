"""#323: generate_form must honor Control.label / Control.help."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field
from tests.unit._helpers_044 import make_app, reset_044

from hedron import Control, FormBody, Page, Text
from hedron_core.rendering import render


def setup_function() -> None:
    reset_044()


class NoteInput(BaseModel):
    title: Annotated[str, Control(label="Note title", help="Keep it short")]
    summary: Annotated[str, Field(title="Summary line")]


def test_generate_form_uses_control_label_and_help() -> None:
    app = make_app()

    @app.command(fallback="/")
    def add_note(data: Annotated[NoteInput, FormBody()]):
        return Text(data.title)

    @app.page("/")
    def home():
        return Page(Text("h"), title="Home")

    markup = render(add_note.form()).html
    assert "Note title" in markup
    assert "Keep it short" in markup
    assert markup.count("Note title") >= 1


def test_generate_form_uses_pydantic_field_title() -> None:
    app = make_app()

    @app.command(fallback="/")
    def add_note(data: Annotated[NoteInput, FormBody()]):
        return Text(data.title)

    markup = render(add_note.form()).html
    assert "Summary line" in markup


def test_generated_command_form_rejects_reserved_attribute_overrides() -> None:
    app = make_app()

    @app.command(fallback="/")
    def add_note(data: Annotated[NoteInput, FormBody()]):
        return Text(data.title)

    markup = render(add_note.form(method="get", action="/untrusted")).html

    assert 'method="post"' in markup
    assert 'hx-post="/_hedron/commands/add-note"' in markup
    assert "/untrusted" not in markup
