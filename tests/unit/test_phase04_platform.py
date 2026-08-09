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
    assert compatible_hedron_version(">=0.4,<=0.4.0", "0.4.0")
    assert not compatible_hedron_version("<=0.3.9", "0.4.0")
    assert not compatible_hedron_version("not-a-spec", "0.4.0")


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
        hedron_version=">=0.25,<0.26",
    )

    def bad(ctx: PluginContext) -> None:
        raise RuntimeError("boom")

    bad.PLUGIN_META = PluginMeta(  # type: ignore[attr-defined]
        name="bad",
        version="0.4.0",
        distribution="bad",
        hedron_version=">=0.25,<0.26",
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


def test_plugin_loader_rolls_back_components_on_failure() -> None:
    reset_registry_for_tests()
    reset_explorer_panels_for_tests()

    def good(ctx: PluginContext) -> None:
        ctx.register_component(
            logical_id="demo:x.Good",
            name="Good",
            module="x",
            distribution="demo",
        )

    good.PLUGIN_META = PluginMeta(  # type: ignore[attr-defined]
        name="good",
        version="0.4.0",
        distribution="good",
        capabilities=PluginCapabilities(python=True),
        hedron_version=">=0.25,<0.26",
    )

    def bad(ctx: PluginContext) -> None:
        raise RuntimeError("component boom")

    bad.PLUGIN_META = PluginMeta(  # type: ignore[attr-defined]
        name="bad",
        version="0.4.0",
        distribution="bad",
        hedron_version=">=0.25,<0.26",
    )

    class EP:
        def __init__(self, name: str, fn: object) -> None:
            self.name = name
            self._fn = fn

        def load(self) -> object:
            return self._fn

    with pytest.raises(RuntimeError, match="component boom"):
        load_plugins(entry_points=[EP("good", good), EP("bad", bad)])
    assert not any(c.name == "Good" for c in get_registry().components())


def test_plugin_enabled_empty_loads_none() -> None:
    reset_registry_for_tests()
    reset_explorer_panels_for_tests()

    def register(ctx: PluginContext) -> None:
        ctx.register_component(
            logical_id="demo:x.Widget",
            name="Widget",
            module="x",
            distribution="demo",
        )

    register.PLUGIN_META = PluginMeta(  # type: ignore[attr-defined]
        name="demo",
        version="0.4.0",
        distribution="demo",
        hedron_version=">=0.25,<0.26",
    )

    class EP:
        name = "demo"

        def load(self) -> object:
            return register

    loader = load_plugins(enabled=[], entry_points=[EP()])
    assert loader.loaded == []
    assert not any(c.name == "Widget" for c in get_registry().components())


def test_plugin_enabled_missing_raises() -> None:
    from hedron_core.diagnostics import HedronError

    class EP:
        name = "demo"

        def load(self) -> object:
            return lambda ctx: None

    with pytest.raises(HedronError) as exc:
        load_plugins(enabled=["missing"], entry_points=[EP()])
    assert exc.value.diagnostic.code == "HED-PLUGIN-0001"


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
        hedron_version=">=0.25,<0.26",
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
    scaffold_toml = (tmp_path / "demoapp" / "pyproject.toml").read_text(encoding="utf-8")
    assert "hedron>=0.25.0" in scaffold_toml
    assert "hedron>=0.25.0,<0.26" in scaffold_toml
    assert "uvicorn[standard]" in scaffold_toml
    assert "0.4.0" not in scaffold_toml

    reset_registry_for_tests()
    register_component(
        logical_id="app:demo.Pill",
        name="Pill",
        module="demo",
        distribution="app",
        styles_path=str(tmp_path / "t.css"),
    )
    (tmp_path / "t.css").write_text(".x { color: red; }", encoding="utf-8")
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


def test_explorer_blocks_path_outside_allowlist(tmp_path: Path) -> None:
    reset_registry_for_tests()
    secret = tmp_path / "secret.txt"
    secret.write_text("TOP_SECRET", encoding="utf-8")
    folder = tmp_path / "components" / "Safe"
    folder.mkdir(parents=True)
    (folder / "styles.css").write_text(".ok { color: green; }", encoding="utf-8")
    register_component(
        logical_id="app:safe.Safe",
        name="Safe",
        module="safe",
        distribution="app",
        styles_path=str(secret),  # points outside folder on purpose
        folder_path=str(folder),
    )
    app = Hedron(
        title="ex",
        security="standard",
        explorer="development",
        session_secret="secret",
    )
    app.state.hedron_component_roots = [str((tmp_path / "components").resolve())]
    with TestClient(app) as client:
        detail = client.get("/hedron-explorer/component/Safe")
        assert detail.status_code == 200
        assert "TOP_SECRET" not in detail.text
        assert "allowlisted" in detail.text or "unavailable" in detail.text
        assert "iframe" in detail.text and "sandbox" in detail.text


def test_explorer_rejects_folder_path_as_root(tmp_path: Path) -> None:
    """Registry folder_path must not expand the filesystem allowlist."""
    reset_registry_for_tests()
    secret = tmp_path / "outside" / "secret.txt"
    secret.parent.mkdir(parents=True)
    secret.write_text("TOP_SECRET", encoding="utf-8")
    folder = tmp_path / "components" / "Safe"
    folder.mkdir(parents=True)
    (folder / "styles.css").write_text(".ok { color: green; }", encoding="utf-8")
    register_component(
        logical_id="app:safe.Safe",
        name="Safe",
        module="safe",
        distribution="app",
        styles_path=str(secret),
        # Attacker-controlled root covering the secret file.
        folder_path=str(tmp_path / "outside"),
    )
    app = Hedron(
        title="ex",
        security="standard",
        explorer="development",
        session_secret="secret",
    )
    app.state.hedron_component_roots = [str((tmp_path / "components").resolve())]
    with TestClient(app) as client:
        detail = client.get("/hedron-explorer/component/Safe")
        assert detail.status_code == 200
        assert "TOP_SECRET" not in detail.text


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
        home = client.get("/")
        assert home.status_code == 200
        token = home.cookies.get("hedron_csrf")
        assert token
        csrf_headers = {"X-CSRF-Token": token}
        index = client.get("/hedron-explorer/")
        assert index.status_code == 200
        assert "Skip to content" in index.text
        assert "Components" in index.text
        css = client.get("/hedron-explorer/static/explorer.css")
        assert css.status_code == 200
        routes = client.get("/hedron-explorer/routes")
        assert routes.status_code == 200
        a11y = client.get("/hedron-explorer/a11y")
        assert a11y.status_code == 200
        api = client.get("/hedron-explorer/api/routes")
        assert api.status_code == 200
        assert "explanations" in api.json()[0]
        missing = client.get("/hedron-explorer/component/DoesNotExist")
        assert missing.status_code == 404
        denied = client.post(
            "/hedron-explorer/api/simulate",
            json={"route": "missing", "allow_mutations": False},
            headers=csrf_headers,
        )
        assert denied.status_code == 400
        bad_json = client.post(
            "/hedron-explorer/api/simulate",
            content=b"{not-json",
            headers={"content-type": "application/json", **csrf_headers},
        )
        assert bad_json.status_code == 400
        unknown_key = client.post(
            "/hedron-explorer/api/simulate",
            json={"route": "home", "extra": 1},
            headers=csrf_headers,
        )
        assert unknown_key.status_code == 400
        mutations = client.post(
            "/hedron-explorer/api/simulate",
            json={"route": "home", "allow_mutations": True},
            headers=csrf_headers,
        )
        assert mutations.status_code == 403
        bare = client.post(
            "/hedron-explorer/api/simulate",
            json={"route": "missing", "allow_mutations": False},
        )
        assert bare.status_code == 403


def test_explorer_simulate_requires_csrf_policy() -> None:
    """Simulate fails closed when hedron_security is missing (no CSRF skip)."""
    from fastapi import FastAPI

    from hedron_explorer import explorer_router

    plain = FastAPI()
    plain.include_router(explorer_router(), prefix="/hedron-explorer")
    with TestClient(plain) as client:
        denied = client.post(
            "/hedron-explorer/api/simulate",
            json={"route": "missing", "allow_mutations": False},
        )
        assert denied.status_code == 403
        assert "CSRF policy" in denied.json()["detail"]


def test_csrf_on_mixed_method_page_and_action() -> None:
    app = Hedron(title="csrf-mixed", security="standard", explorer="off", session_secret="secret")

    @app.page("/form", methods=["GET", "POST"])
    def form_page() -> Page:
        return Page(Text("form"), title="Form")

    @app.action("/act", methods=["GET", "POST"])
    def act() -> Text:
        return Text("ok")

    with TestClient(app) as client:
        get_ok = client.get("/form")
        assert get_ok.status_code == 200
        denied_page = client.post("/form", data={"x": "1"})
        assert denied_page.status_code == 403
        token = get_ok.cookies.get("hedron_csrf")
        assert token
        ok_page = client.post("/form", data={"x": "1", "csrf_token": token})
        assert ok_page.status_code == 200
        denied_action = client.post("/act", data={"x": "1"})
        assert denied_action.status_code == 403
        ok_action = client.post("/act", data={"x": "1", "csrf_token": token})
        assert ok_action.status_code == 200


def test_sample_kit_plugin_module() -> None:
    from hedron_sample_kit.components.Callout import Callout, default
    from hedron_sample_kit.plugin import PLUGIN_META, register

    reset_registry_for_tests()
    reset_explorer_panels_for_tests()
    ctx = PluginContext(PLUGIN_META)
    register(ctx)
    callout_meta = next(c for c in get_registry().components() if c.name == "Callout")
    assert callout_meta.styles_path is not None
    assert Path(callout_meta.styles_path).name == "styles.css"
    assert Path(callout_meta.styles_path).is_file()
    assert any(p.panel_id == "sample-kit-callout" for p in get_explorer_panels())
    assert any(a.logical_id.endswith("callout.mark") for a in get_registry().assets())
    rendered = render_html(Callout(message="hi"))
    assert "hi" in rendered
    assert default().props.message
