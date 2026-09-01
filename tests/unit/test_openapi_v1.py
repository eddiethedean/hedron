"""Canonical Hedron 1.0 OpenAPI projection contracts."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel

from hedron import FormBody, Hedron, RequiresScopes, Text
from hedron.openapi import operation_id_for


def _app() -> Hedron:
    return Hedron(
        title="OpenAPI v1",
        security="development",
        explorer="off",
        session_secret="openapi-v1-test-secret",
    )


def _operation(schema: dict[str, object], path: str, method: str) -> dict[str, object]:
    paths = schema.get("paths")
    assert isinstance(paths, dict)
    path_item = paths[path]
    assert isinstance(path_item, dict)
    operation = path_item[method]
    assert isinstance(operation, dict)
    return operation


def test_operation_id_normalizes_root_parameters_and_method() -> None:
    assert operation_id_for("view", "home", "/", "GET") == "hedron_view_home_get_root"
    assert (
        operation_id_for("action", "save", "/teams/{team_id}/items", "PATCH")
        == "hedron_action_save_patch_teams_team_id_items"
    )


def test_v1_view_openapi_emits_hedron_and_html_contracts() -> None:
    app = _app()

    @app.view("/status", include_in_schema=True)
    def status() -> object:
        return Text("ready")

    app.state.hedron_interactions = app.interactions
    expected = app.state.hedron_interactions.require(status.logical_id).descriptor_fingerprint
    app.openapi_schema = None
    schema = app.openapi()
    operation = _operation(schema, "/status", "get")

    assert operation["x-hedron-kind"] == "view"
    assert operation["x-hedron-logical-id"] == status.logical_id
    assert operation["x-hedron-descriptor-fingerprint"] == expected
    assert operation["x-hedron-htmx"]
    responses = operation["responses"]
    assert isinstance(responses, dict)
    assert "text/html" in responses["200"]["content"]


def test_v1_action_openapi_emits_type_schema_and_scope_declaration() -> None:
    app = _app()

    class Payload(BaseModel):
        name: str

    @app.action(
        "/save",
        fallback="/",
        authorization=RequiresScopes("write"),
    )
    def save(data: Annotated[Payload, FormBody()]) -> object:
        return Text(data.name)

    app.state.hedron_interactions = app.interactions
    app.openapi_schema = None
    schema = app.openapi()
    operation = _operation(schema, "/save", "post")

    assert operation["x-hedron-kind"] == "action"
    assert operation["security"] == [{"hedronScopes": ["write"]}]
    assert "x-hedron-input-schema" in operation
    assert "x-hedron-output-schema" in operation
    components = schema["components"]
    assert isinstance(components, dict)
    schemes = components["securitySchemes"]
    assert isinstance(schemes, dict)
    assert schemes["hedronScopes"]["name"] == "X-Hedron-Scopes"


def test_openapi_schema_is_cached_without_rebuilding() -> None:
    app = _app()

    @app.action("/ping")
    def ping() -> object:
        return Text("pong")

    first = app.openapi()
    second = app.openapi()
    assert second is first
