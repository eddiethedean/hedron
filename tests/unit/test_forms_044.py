"""FORM-044: ActionHandle.form() and closed control inventory."""

from __future__ import annotations

from typing import Annotated, Literal

import pytest
from pydantic import BaseModel, Field
from tests.unit._helpers_044 import csrf_headers, make_app, reset_044

from hedron import Control, FormBody, Page, Text
from hedron_core.codes import HED_TYPE_0005
from hedron_core.diagnostics import HedronError
from hedron_core.rendering import render


def setup_function() -> None:
    reset_044()


class AddNoteInput(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=80), Control(label="Title")]
    body: Annotated[str, Field(max_length=4000), Control(kind="textarea", label="Note")]
    urgent: bool = False


def test_form_generation_native_controls() -> None:
    app = make_app()

    @app.command(fallback="/")
    def add_note(data: Annotated[AddNoteInput, FormBody()]):
        return Text(data.title)

    markup = render(add_note.form()).html
    assert "<form" in markup
    assert 'type="hidden"' in markup or "csrf" in markup.lower() or "hedron_csrf" in markup
    assert "textarea" in markup
    assert 'type="checkbox"' in markup or "checkbox" in markup
    assert "guessed" not in markup


def test_unknown_control_kind_fails() -> None:
    with pytest.raises(HedronError) as caught:
        Control(kind="fancy-widget")
    assert caught.value.diagnostics[0].code == HED_TYPE_0005


def test_rejected_dict_cannot_generate() -> None:
    app = make_app()

    class Bad(BaseModel):
        extra: dict[str, str]

    with pytest.raises(HedronError) as caught:

        @app.command(fallback="/")
        def nope(data: Annotated[Bad, FormBody()]):
            return Text("no")

    assert caught.value.diagnostics[0].code == HED_TYPE_0005


def test_unmodeled_command_has_no_form() -> None:
    app = make_app()

    @app.command(fallback="/")
    def ping():
        return Text("pong")

    with pytest.raises(HedronError) as caught:
        ping.form()
    assert caught.value.diagnostics[0].code == HED_TYPE_0005


def test_enum_select_supported() -> None:
    app = make_app()

    class ChoiceIn(BaseModel):
        color: Literal["red", "blue"]

    @app.command(fallback="/")
    def choose(data: Annotated[ChoiceIn, FormBody()]):
        return Text(data.color)

    markup = render(choose.form()).html
    assert "<select" in markup
    assert "red" in markup


def test_form_field_alias_is_the_posted_name() -> None:
    from fastapi.testclient import TestClient

    app = make_app()

    class Aliased(BaseModel):
        title: Annotated[str, Field(alias="song_title")]

    @app.command(fallback="/")
    def add(data: Annotated[Aliased, FormBody()]):
        return Text(data.title)

    @app.page("/")
    def home():
        return Page(Text("h"), title="H")

    markup = render(add.form()).html
    assert 'name="song_title"' in markup
    client = TestClient(app)
    posted = client.post(
        add.path,
        data={"song_title": "hello"},
        headers=csrf_headers(client),
    )
    assert posted.status_code == 200
    assert "hello" in posted.text
