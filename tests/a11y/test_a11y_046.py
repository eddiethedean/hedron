"""A11Y-046: native fallback; chart alternatives; no Supported human AT claim."""

from __future__ import annotations

from typing import Annotated

from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from tests.unit._helpers_046 import make_app, reset_046

from hedron import Control, FormBody, Page, Text
from hedron_core.rendering import render
from hedron_data import DataWorkspace, DataWorkspacePolicy, InMemoryDataSource


def setup_function() -> None:
    reset_046()


class NoteIn(BaseModel):
    title: Annotated[str, Field(min_length=1), Control(label="Title")]


class Row(BaseModel):
    id: str
    title: str = "n"


def test_workspace_list_is_native_table() -> None:
    app = make_app()
    workspace = DataWorkspace(
        name="notes",
        model=Row,
        source=InMemoryDataSource([{"id": "1", "title": "n"}], key_field="id"),
        policy=DataWorkspacePolicy(can_read=lambda: True),
    )
    app.include_feature(workspace)

    @app.page("/")
    def home():
        return Page(workspace.list_view(), title="Notes")  # type: ignore[misc]

    html = TestClient(app).get("/").text
    assert "<table" in html
    assert "javascript:" not in html.lower()


def test_forms_remain_no_js_and_claim_honest() -> None:
    app = make_app(explorer="development")

    @app.command(fallback="/")
    def add(data: Annotated[NoteIn, FormBody()]):
        return Text(data.title)

    html = render(add.form()).html
    assert "<form" in html
    assert "<label" in html
    assert "Supported human AT" not in html
    explorer = TestClient(app).get("/hedron-explorer/features").text
    assert "SR-021" not in explorer
    assert "Supported human AT" not in explorer
