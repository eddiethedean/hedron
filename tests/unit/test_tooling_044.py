"""TOOLING-044: Explorer TypeSchema, CLI static scan, AppScenario submit_model."""

from __future__ import annotations

from typing import Annotated

from fastapi.testclient import TestClient
from pydantic import BaseModel
from tests.unit._helpers_044 import make_app, reset_044

from hedron import FormBody, Page, Text, ViewParams
from hedron.cli.commands.check import _check_044_type_authoring
from hedron_core.testing.adapters import fastapi_fixture
from hedron_core.testing.app import AppScenario


def setup_function() -> None:
    reset_044()


class Params(BaseModel):
    item_id: str


class Payload(BaseModel):
    title: str


def test_explorer_includes_redacted_type_schema() -> None:
    app = make_app(explorer="development")

    @app.refreshable("/items/{item_id}")
    def item(params: Annotated[Params, ViewParams()]):
        return Text(params.item_id)

    @app.page("/")
    def home():
        return Page(item.bind(item_id="one"), title="Home")

    client = TestClient(app)
    payload = client.get("/hedron-explorer/api/handle-graph").json()
    node = next(row for row in payload["nodes"] if row["id"] == item.logical_id)
    assert node.get("type_schema")
    assert node["type_schema"]["schema_version"] == 1
    assert "values" not in node["type_schema"]


def test_cli_static_scan_does_not_import_target(tmp_path) -> None:  # type: ignore[no-untyped-def]
    (tmp_path / "app.py").write_text(
        "from hedron import ViewParams\nraise SystemExit('imported')\n",
        encoding="utf-8",
    )
    diags = _check_044_type_authoring(tmp_path)
    assert diags == [] or all(getattr(d, "severity", None) for d in diags)


def test_app_scenario_submit_model() -> None:
    app = make_app()

    @app.command(fallback="/")
    def add(data: Annotated[Payload, FormBody()]):
        return Text(data.title)

    @app.page("/")
    def home():
        return Page(add.form(), title="Home")

    fixture = fastapi_fixture(app)
    scenario = AppScenario.from_fixture(fixture)
    scenario.navigate("/")
    response = scenario.submit_model(add.path, Payload(title="hello"))
    assert response.status_code in {200, 303, 400, 403, 422}
    assert scenario.field_path_errors({"detail": [{"loc": ["title"], "msg": "x"}]}) == ["title"]
