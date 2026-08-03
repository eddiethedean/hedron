"""Phase 0.4 platform regression tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from hedron import Hedron, Page, Text
from hedron.cli import main
from hedron.plugins import compatible_hedron_version, load_plugins
from hedron.testing import assert_renders, normalize_snapshot_html, render_html
from hedron_core.plugins import (
    PluginCapabilities,
    PluginContext,
    PluginMeta,
    get_explorer_panels,
    reset_explorer_panels_for_tests,
)
from hedron_core.registry import get_registry, register_component, reset_registry_for_tests


def test_compatible_hedron_version() -> None:
    assert compatible_hedron_version(">=0.4,<0.5", "0.4.0")
    assert not compatible_hedron_version(">=0.4,<0.5", "0.5.0")
    assert not compatible_hedron_version(">=0.4,<0.5", "0.3.9")


def test_plugin_loader_registers_panel_and_rolls_back_on_failure() -> None:
    reset_registry_for_tests()
    reset_explorer_panels_for_tests()

    def good(ctx: PluginContext) -> None:
        ctx.register_explorer_panel(
            panel_id="good-panel",
            title="Good",
            description="ok",
        )

    good.PLUGIN_META = PluginMeta(  # type: ignore[attr-defined]
        name="good",
        version="0.4.0",
        distribution="good",
        capabilities=PluginCapabilities(explorer_panels=True),
    )

    def bad(ctx: PluginContext) -> None:
        raise RuntimeError("boom")

    bad.PLUGIN_META = PluginMeta(  # type: ignore[attr-defined]
        name="bad",
        version="0.4.0",
        distribution="bad",
    )

    class EP:
        def __init__(self, name: str, fn: object) -> None:
            self.name = name
            self._fn = fn

        def load(self) -> object:
            return self._fn

    with pytest.raises(RuntimeError, match="boom"):
        load_plugins(entry_points=[EP("good", good), EP("bad", bad)])
    assert get_explorer_panels() == ()


def test_plugin_loader_success() -> None:
    reset_registry_for_tests()
    reset_explorer_panels_for_tests()

    def register(ctx: PluginContext) -> None:
        ctx.register_component(
            logical_id="demo:x.Widget",
            name="Widget",
            module="x",
            distribution="demo",
        )
        ctx.register_explorer_panel(panel_id="demo-panel", title="Demo")

    register.PLUGIN_META = PluginMeta(  # type: ignore[attr-defined]
        name="demo",
        version="0.4.0",
        distribution="demo",
        capabilities=PluginCapabilities(python=True, explorer_panels=True),
    )

    class EP:
        name = "demo"

        def load(self) -> object:
            return register

    loader = load_plugins(entry_points=[EP()])
    assert any(c.name == "Widget" for c in get_registry().components())
    assert any(p.panel_id == "demo-panel" for p in get_explorer_panels())
    loader.start()
    loader.shutdown()


def test_cli_new_check_graph_audit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as new_exc:
        main(["new", "demoapp", "--path", str(tmp_path / "demoapp")])
    assert new_exc.value.code == 0
    assert (tmp_path / "demoapp" / "app.py").is_file()

    reset_registry_for_tests()
    register_component(
        logical_id="app:demo.Pill",
        name="Pill",
        module="demo",
        distribution="app",
        hdn_source=str(tmp_path / "t.hdn"),
    )
    (tmp_path / "t.hdn").write_text("<div>x</div>", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[tool.hedron]\n", encoding="utf-8")

    with pytest.raises(SystemExit) as graph_exc:
        main(["graph"])
    assert graph_exc.value.code == 0

    with pytest.raises(SystemExit) as audit_exc:
        main(["audit-components"])
    assert audit_exc.value.code == 0

    with pytest.raises(SystemExit) as check_exc:
        main(["check", "--format", "json", "--severity", "error"])
    assert check_exc.value.code == 0


def test_testing_helpers_render() -> None:
    html = render_html(Text("hello"))
    assert "hello" in html
    assert_renders(Text("world"), contains="world")
    assert "<asset>" in normalize_snapshot_html("/hedron-assets/foo.abc123.css")


def test_explorer_panels_and_simulate() -> None:
    app = Hedron(
        title="ex",
        security="standard",
        explorer="development",
        session_secret="secret",
    )

    @app.page("/")
    def home() -> Page:
        return Page(Text("hi"), title="T")

    with TestClient(app) as client:
        index = client.get("/hedron-explorer/")
        assert index.status_code == 200
        assert "Skip to content" in index.text
        assert "Components" in index.text
        routes = client.get("/hedron-explorer/routes")
        assert routes.status_code == 200
        a11y = client.get("/hedron-explorer/a11y")
        assert a11y.status_code == 200
        api = client.get("/hedron-explorer/api/routes")
        assert api.status_code == 200
        assert "explanations" in api.json()[0]
        denied = client.post(
            "/hedron-explorer/api/simulate",
            json={"route": "missing", "allow_mutations": False},
        )
        assert denied.status_code == 400
        mutations = client.post(
            "/hedron-explorer/api/simulate",
            json={"route": "home", "allow_mutations": True},
        )
        assert mutations.status_code == 403


def test_sample_kit_plugin_module() -> None:
    from hedron_sample_kit.plugin import PLUGIN_META, register

    reset_registry_for_tests()
    reset_explorer_panels_for_tests()
    ctx = PluginContext(PLUGIN_META)
    register(ctx)
    assert any(c.name == "Callout" for c in get_registry().components())
    assert any(p.panel_id == "sample-kit-callout" for p in get_explorer_panels())
