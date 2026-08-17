"""TOOLING-048 Explorer, CLI, HDJ, catalog facts without executing JS."""

from __future__ import annotations

from tests.unit._helpers_046 import make_app, with_client

from hedron.cli.commands.inspect import _cmd_inspect_htmx_extensions
from hedron_core.htmx_extensions import catalog_facts
from hedron_explorer.router import explorer_router
from hedron_jinja import ExtensionRegistry, register_htmx_catalog


def test_catalog_facts_are_inert() -> None:
    facts = catalog_facts()
    assert facts["hx_ext_never_installs"] is True
    for item in facts["extensions"]:
        assert item["executes_untrusted_code"] is False


def test_hdj_projection_and_cli() -> None:
    registry = register_htmx_catalog(ExtensionRegistry())
    assert registry.get("sse") is not None
    assert registry.get("htmx-ext-sse") is None

    class _Args:
        json = True

    assert _cmd_inspect_htmx_extensions(_Args()) == 0


def test_explorer_extensions_route() -> None:
    paths = [getattr(route, "path", "") for route in explorer_router().routes]
    assert "/extensions" in paths

    def _check(client) -> None:
        response = client.get("/hedron-explorer/extensions")
        assert response.status_code == 200
        assert b"without executing untrusted" in response.content
        assert b"head-support" in response.content
        assert b"morph_admitted" in response.content

    from hedron import Page, Text

    app = make_app(explorer="development")

    @app.page("/")
    def home():
        return Page(Text("ok"), title="Home")

    with_client(app, _check)
