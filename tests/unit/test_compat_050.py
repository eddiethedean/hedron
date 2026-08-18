"""COMPAT-050 0.49 consumers still mount; ExplorerPanelMeta shim."""

from __future__ import annotations

from fastapi.testclient import TestClient
from tests.unit._helpers_050 import make_app, reset_050

from hedron import FormBody, Page, Text
from hedron_core.plugins import ExplorerPanelMeta, get_explorer_panels, register_explorer_panel


def setup_function() -> None:
    reset_050()


def test_049_form_and_actionhandle_still_work() -> None:
    from typing import Annotated

    from pydantic import BaseModel

    app = make_app(security="standard", explorer="development")

    class Payload(BaseModel):
        title: str = "ok"

    @app.command(fallback="/")
    def save(data: Annotated[Payload, FormBody()]):
        return Text(data.title)

    @app.page("/")
    def home():
        return Page(save.form(), title="Form")

    with TestClient(app) as client:
        page = client.get("/")
        assert page.status_code == 200
        assert "<form" in page.text
        explorer = client.get("/hedron-explorer/")
        assert explorer.status_code == 200
        assert client.get("/hedron-explorer/api/routes").status_code == 200


def test_panel_meta_register_still_works() -> None:
    register_explorer_panel(panel_id="compat-panel", title="Compat", plugin="compat")
    panels = get_explorer_panels()
    assert any(isinstance(p, ExplorerPanelMeta) and p.panel_id == "compat-panel" for p in panels)
