"""CLASS-044: RefreshableView / CommandHandler compile to the same handles."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel
from tests.unit._helpers_044 import make_app, reset_044

from hedron import CommandHandler, Page, RefreshableView, Text, ViewParams


def setup_function() -> None:
    reset_044()


class ItemParams(BaseModel):
    item_id: str = "one"


class ItemView(RefreshableView[ItemParams, str]):
    def load(self, params: Annotated[ItemParams, ViewParams()]) -> str:
        return params.item_id

    def render(self, data: str):
        return Text(data)


class Ping(CommandHandler[None, object]):
    fallback = "/"

    def execute(self):
        return Text("pong")


def test_class_view_registers_handle() -> None:
    app = make_app()
    handle = app.refreshable(ItemView)

    @app.page("/")
    def home():
        return Page(handle(), title="Home")

    from fastapi.testclient import TestClient

    client = TestClient(app)
    page = client.get("/")
    assert page.status_code == 200
    assert handle.logical_id.lower().startswith("item") or "ItemView" in handle.name
    bound = handle.bind(item_id="z")
    assert bound.handle.bound


def test_class_command_registers_handle() -> None:
    app = make_app()
    cmd = app.command(Ping)
    assert cmd.fallback == "/"
    assert cmd.path.startswith("/_hedron/commands/")


def test_function_class_schema_equivalence() -> None:
    app = make_app()

    @app.refreshable
    def item_fn(params: Annotated[ItemParams, ViewParams()]):
        return Text(params.item_id)

    class_handle = app.refreshable(ItemView)
    assert item_fn.schema is not None and class_handle.schema is not None
    assert item_fn.schema.boundary_sources == class_handle.schema.boundary_sources
