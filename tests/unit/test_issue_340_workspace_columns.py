"""#340: DataWorkspace.columns and form_overrides must apply."""

from __future__ import annotations

from fastapi.testclient import TestClient
from pydantic import BaseModel
from tests.unit._helpers_046 import make_app, reset_046

from hedron import Page, Text, render
from hedron_core import RenderMode
from hedron_data import DataWorkspace, DataWorkspacePolicy, InMemoryDataSource


def setup_function() -> None:
    reset_046()


class Row(BaseModel):
    id: str
    title: str = "n"


def test_columns_omit_extra_source_fields_and_form_overrides_apply() -> None:
    app = make_app()
    ws = DataWorkspace(
        name="notes",
        model=Row,
        source=InMemoryDataSource(
            [{"id": "1", "title": "hello", "hidden": "SECRET"}],
            key_field="id",
        ),
        policy=DataWorkspacePolicy(can_read=lambda: True, can_create=lambda: True),
        columns=["title"],
        form_overrides={"title": Text("Buyer-override")},
    )
    app.include_feature(ws)

    @app.page("/")
    def home():
        return Page(ws.list_view(), title="Notes")  # type: ignore[misc]

    html = TestClient(app).get("/").text
    assert "hello" in html
    assert "SECRET" not in html
    form_html = render(ws.create_command.form(), mode=RenderMode.FRAGMENT).html  # type: ignore[union-attr]
    assert "Buyer-override" in form_html
    assert "SECRET" not in form_html
