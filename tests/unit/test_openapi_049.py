"""OPENAPI-049 typed projection without replacing HTML routes."""

from __future__ import annotations

from tests.unit._helpers_049 import make_app, reset_049

from hedron import RequiresScopes, Text
from hedron.openapi import operation_id_for


def setup_function() -> None:
    reset_049()


def test_operation_ids_stay_stable() -> None:
    assert operation_id_for("view", "items", "/items", "GET").startswith("hedron_view_items_get")


def test_html_routes_keep_text_html_and_scopes_do_not_grant() -> None:
    app = make_app()

    @app.view("/page", include_in_schema=True)
    def page():
        return Text("hello")

    @app.action(
        "/export",
        fallback="/",
        include_in_schema=True,
        authorization=RequiresScopes("read"),
    )
    def export():
        return Text("done")

    schema = app.openapi()
    assert isinstance(schema, dict)
    found_html = False
    for path_item in (schema.get("paths") or {}).values():
        if not isinstance(path_item, dict):
            continue
        for operation in path_item.values():
            if not isinstance(operation, dict):
                continue
            content = ((operation.get("responses") or {}).get("200") or {}).get("content") or {}
            if "text/html" in content:
                found_html = True
            if operation.get("security"):
                assert RequiresScopes("read").grants_access() is False
                schemes = (schema.get("components") or {}).get("securitySchemes") or {}
                assert "hedronScopes" in schemes
    assert found_html
    assert RequiresScopes("read").scopes == ("read",)
    assert export.path
    op = (schema.get("paths") or {}).get("/export", {}).get("post") or {}
    assert op.get("security") == [{"hedronScopes": ["read"]}]
    assert "x-hedron-input-schema" in op or op.get("x-hedron-kind") == "action"


def test_modeled_command_emits_type_schema_and_security_scheme() -> None:
    from typing import Annotated

    from pydantic import BaseModel

    from hedron import FormBody, RequiresScopes, Text

    app = make_app()

    class Payload(BaseModel):
        name: str

    @app.action(
        "/save",
        fallback="/",
        include_in_schema=True,
        authorization=RequiresScopes("write"),
    )
    def save(data: Annotated[Payload, FormBody()]):
        return Text(data.name)

    schema = app.openapi()
    op = ((schema.get("paths") or {}).get("/save") or {}).get("post") or {}
    assert op.get("security") == [{"hedronScopes": ["write"]}]
    schemes = (schema.get("components") or {}).get("securitySchemes") or {}
    assert "hedronScopes" in schemes
    assert "x-hedron-input-schema" in op
