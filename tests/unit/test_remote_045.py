"""REMOTE-045: MCP/Gradio consume catalog facts without auto-exposure."""

from __future__ import annotations

from tests.unit._helpers_045 import make_app, reset_045

from hedron import Text
from hedron_core.catalog import compile_interaction_catalog
from hedron_gradio import GradioClientAdapter
from hedron_mcp import McpProjection


def setup_function() -> None:
    reset_045()


def test_mcp_catalog_presence_does_not_enable_or_expose() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    catalog = compile_interaction_catalog(app_id=app.hedron_app_id)
    projection = McpProjection()
    ids = projection.consume_catalog(catalog)
    assert status.logical_id in ids
    assert projection.enabled is False
    assert projection.tools == ()
    assert projection.resources == ()


def test_gradio_catalog_presence_does_not_enable() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    catalog = compile_interaction_catalog(app_id=app.hedron_app_id)
    adapter = GradioClientAdapter(base_url="http://127.0.0.1:1")
    ids = adapter.consume_catalog(catalog)
    assert status.logical_id in ids
    assert adapter.enabled is False
    assert adapter.discover() == []
