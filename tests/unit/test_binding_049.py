"""BINDING-049 native-model versus expanded-fields."""

from __future__ import annotations

from typing import Annotated

from fastapi.testclient import TestClient
from pydantic import BaseModel
from tests.unit._helpers_049 import make_app, reset_049

from hedron import FormBody, Text, ViewParams
from hedron.type_authoring.binding import boundary_plan_for
from hedron.type_authoring.normalize import inspect_handler


def setup_function() -> None:
    reset_049()


class Filters(BaseModel):
    q: str = ""
    limit: int = 10


class Item(BaseModel):
    item_id: str
    q: str = ""


class Payload(BaseModel):
    title: str


def test_query_only_is_native_model() -> None:
    def items(filters: Annotated[Filters, ViewParams(source="query")]):
        return filters

    compiled = inspect_handler(items, kind="view", path="/items")
    plan = boundary_plan_for(compiled)
    assert plan.strategy == "native-model"
    assert plan.structural.path_params == ()


def test_query_only_http_binds_query_string_not_json_body() -> None:
    app = make_app()

    @app.refreshable("/items", include_in_schema=True)
    def items(filters: Annotated[Filters, ViewParams(source="query")]):
        return Text(filters.q or "all")

    with TestClient(app) as client:
        matched = client.get("/items", params={"q": "hello"})
        defaults = client.get("/items")

    assert matched.status_code == 200
    assert "hello" in matched.text
    assert defaults.status_code == 200
    assert "all" in defaults.text
    operation = app.openapi()["paths"]["/items"]["get"]
    assert "requestBody" not in operation
    parameters = {item["name"]: item["in"] for item in operation.get("parameters") or []}
    assert parameters.get("q") == "query"


def test_mixed_path_query_stays_expanded() -> None:
    def item(params: Annotated[Item, ViewParams()]):
        return params

    compiled = inspect_handler(item, kind="view", path="/items/{item_id}")
    plan = boundary_plan_for(compiled)
    assert plan.strategy == "expanded-fields"
    assert plan.fallback_reason == "mixed-path-query"
    assert "item_id" in plan.structural.path_params


def test_author_override_and_portable_adapters() -> None:
    def items(filters: Annotated[Filters, ViewParams(source="query")]):
        return filters

    compiled = inspect_handler(items, kind="view")
    forced = boundary_plan_for(compiled, force_expanded=True)
    assert forced.strategy == "expanded-fields"
    assert forced.fallback_reason == "author-override"
    portable = boundary_plan_for(compiled, flask_django=True)
    assert portable.strategy == "expanded-fields"
    assert portable.adapter_disposition == "projection_adapter"


def test_existing_formbody_keeps_working() -> None:
    app = make_app()

    @app.command(fallback="/")
    def save(data: Annotated[Payload, FormBody()]):
        return Text(data.title)

    compiled = inspect_handler(save.handler, kind="command")
    plan = boundary_plan_for(compiled)
    assert plan.strategy == "expanded-fields"
    assert plan.fallback_reason == "form-not-equivalent"
    assert save.path
