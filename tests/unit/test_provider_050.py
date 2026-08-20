"""PROVIDER-050 ExplorerProvider v1 beside ExplorerPanelMeta."""

from __future__ import annotations

from tests.unit._helpers_050 import reset_050

from hedron_core.plugins import (
    ExplorerPanelMeta,
    ExplorerProvider,
    PluginContext,
    PluginMeta,
    get_explorer_panels,
    get_explorer_providers,
    register_explorer_panel,
    register_explorer_provider,
)
from hedron_explorer.services.provider import run_isolated


def setup_function() -> None:
    reset_050()


def test_provider_does_not_add_fields_to_panel_meta() -> None:
    fields = set(ExplorerPanelMeta.__dataclass_fields__)
    assert fields == {"panel_id", "title", "plugin", "description", "path"}
    provider_fields = set(ExplorerProvider.__dataclass_fields__)
    assert "capabilities" in provider_fields
    assert "timeout_ms" in provider_fields


def test_register_provider_upserts_panel() -> None:
    register_explorer_provider(
        ExplorerProvider(
            panel_id="demo",
            title="Demo",
            plugin="demo",
            path="/hedron-explorer/packages",
        )
    )
    panels = get_explorer_panels()
    assert any(p.panel_id == "demo" for p in panels)
    assert get_explorer_providers()[0].panel_id == "demo"


def test_context_stamps_plugin_name() -> None:
    ctx = PluginContext(
        PluginMeta(
            name="third-party",
            version="1.0.0",
            distribution="third-party",
            hedron_version=">=0.52,<0.53",
        )
    )
    ctx.register_explorer_provider(panel_id="tp", title="TP")
    assert get_explorer_providers()[0].plugin == "third-party"


def test_meta_only_gets_conservative_defaults() -> None:
    register_explorer_panel(panel_id="meta", title="Meta", plugin="x")
    from hedron_explorer.services.provider import providers_or_defaults

    wrapped = {p.panel_id: p for p in providers_or_defaults()}
    assert wrapped["meta"].timeout_ms == 250


def test_crash_and_payload_isolation() -> None:
    provider = ExplorerProvider(panel_id="boom", title="Boom", plugin="x", max_payload_bytes=8)

    crashed = run_isolated(provider, lambda: (_ for _ in ()).throw(RuntimeError("nope")))
    assert crashed["ok"] is False
    assert crashed["isolated"] is True

    huge = run_isolated(provider, lambda: "x" * 64)
    assert huge["ok"] is False
    assert huge["diagnostic"] == "HED-EXPLORER-0003"


def test_packages_page_isolates_crashing_provider() -> None:
    from fastapi.testclient import TestClient
    from tests.unit._helpers_050 import make_app

    from hedron import Page, Text

    def _boom() -> str:
        raise RuntimeError("boom")

    register_explorer_provider(
        ExplorerProvider(panel_id="crashy", title="Crashy", plugin="demo", render=_boom)
    )
    app = make_app(security="standard", explorer="development")

    @app.page("/")
    def home():
        return Page(Text("h"), title="H")

    with TestClient(app) as client:
        page = client.get("/hedron-explorer/packages")
        assert page.status_code == 200
        assert "HED-EXPLORER-0002" in page.text
        assert "Crashy" in page.text
