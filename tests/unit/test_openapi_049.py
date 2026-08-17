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

    @app.refreshable("/page", include_in_schema=True)
    def page():
        return Text("hello")

    @app.command(
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
    assert found_html
    assert RequiresScopes("read").scopes == ("read",)
    assert export.path
