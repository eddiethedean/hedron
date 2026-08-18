"""#331: OutcomeMap case status and effects must reach the HTTP response."""

from __future__ import annotations

from typing import Annotated, Literal

from fastapi.testclient import TestClient
from pydantic import BaseModel
from tests.unit._helpers_044 import make_app, reset_044

from hedron import CommandHandler, FormBody, OutcomeMap, Page, Refreshes, Text, case


def setup_function() -> None:
    reset_044()


class Flags(BaseModel):
    urgent: bool = False


class Saved(BaseModel):
    kind: Literal["saved"] = "saved"
    id: str


def test_mapped_status_is_http_status() -> None:
    app = make_app()
    mapping = OutcomeMap(case(Saved, render=lambda item: Text(f"ok:{item.id}"), status=409))

    class SaveIt(CommandHandler):
        outcomes = mapping
        fallback = "/"

        def execute(self, data: Annotated[Flags, FormBody()]) -> Saved:
            return Saved(id="9")

    @app.page("/")
    def home():
        return Page(Text("h"), title="Home")

    handle = app.command(SaveIt)
    client = TestClient(app)
    token = client.get("/").cookies.get("hedron_csrf") or ""
    response = client.post(
        handle.path,
        data={"urgent": "false"},
        headers={"X-CSRF-Token": token, "HX-Request": "true"},
    )
    assert response.status_code == 409
    assert "ok:9" in response.text


def test_mapped_effects_emit_refresh_trigger() -> None:
    app = make_app()

    @app.refreshable
    def notes():
        return Text("notes")

    mapping = OutcomeMap(
        case(
            Saved,
            render=lambda item: Text(f"ok:{item.id}"),
            status=201,
            effects=Refreshes(notes),
        )
    )

    class SaveIt(CommandHandler):
        outcomes = mapping
        effects = Refreshes(notes)
        fallback = "/"

        def execute(self, data: Annotated[Flags, FormBody()]) -> Saved:
            return Saved(id="9")

    @app.page("/")
    def home():
        return Page(notes(), title="Home")

    handle = app.command(SaveIt)
    client = TestClient(app)
    token = client.get("/").cookies.get("hedron_csrf") or ""
    response = client.post(
        handle.path,
        data={"urgent": "false"},
        headers={"X-CSRF-Token": token, "HX-Request": "true"},
    )
    assert response.status_code == 201
    trigger = response.headers.get("HX-Trigger") or ""
    assert "hedron:refresh" in trigger
