"""Regression tests for phase 0.3.0 deep-dive hardening."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request

from hedron import Hedron, Page, Text
from hedron.lifespan import compose_lifespan
from hedron.security.csrf import csrf_token_for_request, ensure_csrf_cookie
from hedron.security.policy import SecurityPolicy
from hedron.static_mount import mount_build_assets
from hedron_core import (
    HedronError,
    compile_css,
)
from hedron_core.compile_gate import force_runtime_compile, set_runtime_compile_allowed
from hedron_core.discovery import apply_discovery_to_registry, discover_component_folders
from hedron_core.registry import get_registry, reset_registry_for_tests


def test_runtime_compile_gate_blocks_and_force_allows(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HEDRON_ENV", "production")
    set_runtime_compile_allowed(True)
    with pytest.raises(HedronError) as css_exc:
        compile_css(".x { color: red; }", component_id="app:x")
    assert css_exc.value.diagnostic.code == "HED-BUILD-0004"
    with force_runtime_compile():
        compile_css(".x { color: red; }", component_id="app:x")
    monkeypatch.delenv("HEDRON_ENV", raising=False)
    set_runtime_compile_allowed(False)
    with pytest.raises(HedronError) as process_exc:
        compile_css(".y { color: blue; }", component_id="app:y")
    assert process_exc.value.diagnostic.code == "HED-BUILD-0004"
    set_runtime_compile_allowed(True)


def test_css_error_diagnostics_raise() -> None:
    with pytest.raises(HedronError) as exc:
        compile_css("html { margin: 0; }", component_id="app:x")
    assert exc.value.diagnostic.code == "HED-CSS-0004"
    with pytest.raises(HedronError) as body_exc:
        compile_css("body { margin: 0; }", component_id="app:x")
    assert body_exc.value.diagnostic.code == "HED-CSS-0004"


def test_css_declaration_without_semicolon() -> None:
    result = compile_css(".x{color:red}", component_id="app:x")
    assert "color: red" in result.css


def test_css_missing_asset_file(tmp_path: Path) -> None:
    root = tmp_path / "comp"
    root.mkdir()
    with pytest.raises(HedronError) as exc:
        compile_css(
            ".x { background: url(missing.png); }",
            component_id="app:x",
            registered_roots=[root],
            component_dir=root,
        )
    assert exc.value.diagnostic.code == "HED-ASSET-0004"


def test_css_symlink_asset_rejected(tmp_path: Path) -> None:
    root = tmp_path / "comp"
    root.mkdir()
    target = tmp_path / "outside.png"
    target.write_bytes(b"png")
    link = root / "icon.png"
    link.symlink_to(target)
    with pytest.raises(HedronError) as exc:
        compile_css(
            ".x { background: url(icon.png); }",
            component_id="app:x",
            registered_roots=[root],
            component_dir=root,
        )
    assert exc.value.diagnostic.code == "HED-ASSET-0002"


def test_css_no_semicolon_url_is_validated(tmp_path: Path) -> None:
    root = tmp_path / "comp"
    root.mkdir()
    (root / "icon.png").write_bytes(b"png")
    result = compile_css(
        ".x { background: url(icon.png) }",
        component_id="app:x",
        registered_roots=[root],
        component_dir=root,
    )
    assert "icon.png" in result.asset_urls
    assert "url(" in result.css


def test_unknown_theme_fails_build(tmp_path: Path) -> None:
    from hedron.build import run_build
    from hedron.config import HedronSettings

    settings = HedronSettings(
        component_roots=("components",),
        build_dir=".hedron/build",
        theme="nope",
        plugins=(),
    )
    (tmp_path / "components").mkdir()
    with pytest.raises(HedronError) as exc:
        run_build(project_dir=tmp_path, settings=settings, production=True)
    assert exc.value.diagnostic.code == "HED-THEME-0001"


def test_production_lifespan_missing_manifest(tmp_path: Path) -> None:
    set_runtime_compile_allowed(True)
    app = FastAPI(lifespan=compose_lifespan(production=True, build_dir=tmp_path / "missing-build"))
    with pytest.raises(HedronError) as exc, TestClient(app):
        pass
    assert exc.value.diagnostic.code == "HED-BUILD-0003"
    set_runtime_compile_allowed(True)


def test_dev_lifespan_starts_without_build_manifest(tmp_path: Path) -> None:
    """Non-production lifespan must not require hedron.build when no manifest exists (#32)."""
    set_runtime_compile_allowed(True)
    app = FastAPI(lifespan=compose_lifespan(production=False, build_dir=tmp_path / "no-build"))
    with TestClient(app) as client:
        assert client.app is app
        assert getattr(app.state, "hedron_build_manifest", None) is None
    set_runtime_compile_allowed(True)


def test_production_lifespan_invalid_manifest(tmp_path: Path) -> None:
    build = tmp_path / "build"
    build.mkdir()
    (build / "manifest.json").write_text('{"format_version": 1}\n', encoding="utf-8")
    set_runtime_compile_allowed(True)
    app = FastAPI(lifespan=compose_lifespan(production=True, build_dir=build))
    with pytest.raises(HedronError) as exc, TestClient(app):
        pass
    assert exc.value.diagnostic.code == "HED-BUILD-0003"
    set_runtime_compile_allowed(True)


def test_csrf_token_for_request_matches_cookie() -> None:
    app = Hedron(title="csrf", security="standard", explorer="off", session_secret="secret")

    @app.page("/")
    def home(request: Request) -> Page:
        policy = request.app.state.hedron_security
        token = csrf_token_for_request(request, policy)
        return Page(Text(token), title="T")

    with TestClient(app) as client:
        response = client.get("/")
        cookie = response.cookies.get("hedron_csrf")
        assert cookie
        assert cookie in response.text
        # Second GET reuses the same token.
        second = client.get("/")
        assert cookie in second.text
        assert second.cookies.get("hedron_csrf") in {None, cookie}


def test_csrf_html_token_post_succeeds_on_first_load() -> None:
    from fastapi import Form

    from hedron.routing import HedronRouter

    app = Hedron(title="csrf", security="standard", explorer="off", session_secret="secret")
    router = HedronRouter()

    @router.page("/seed")
    def seed(request: Request) -> Page:
        policy = request.app.state.hedron_security
        token = csrf_token_for_request(request, policy)
        return Page(Text(f"token={token}"), title="S")

    @router.action("/do", method="POST")
    def do_action(note: str = Form("ok")) -> Text:
        return Text(note)

    app.include_router(router)
    with TestClient(app) as client:
        seeded = client.get("/seed")
        cookie = seeded.cookies.get("hedron_csrf")
        match = re.search(r"token=([A-Za-z0-9_-]+)", seeded.text)
        assert cookie and match
        html_token = match.group(1)
        assert html_token == cookie
        ok = client.post("/do", headers={"X-CSRF-Token": html_token}, data={"note": "done"})
        assert ok.status_code == 200
        assert "done" in ok.text


def test_strict_csrf_secure_flag_follows_scheme() -> None:
    from starlette.responses import Response

    policy = SecurityPolicy.from_name("strict")
    https_app = Hedron(title="s", security="strict", explorer="off", session_secret="secret")

    @https_app.page("/")
    def home() -> Page:
        return Page(Text("ok"), title="T")

    with TestClient(https_app, base_url="https://testserver") as client:
        response = client.get("/")
        assert "Secure" in (response.headers.get("set-cookie") or "")

    # Strict always emits Secure cookies, even for plain HTTP requests.
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [],
        "scheme": "http",
        "server": ("testserver", 80),
        "client": ("127.0.0.1", 123),
    }
    request = Request(scope)
    request.state.hedron_csrf_token = "abc"
    response = Response("ok")
    ensure_csrf_cookie(response, policy, token="abc", request=request)
    header = response.headers.get("set-cookie") or ""
    assert "hedron_csrf=abc" in header
    assert "Secure" in header


def test_asset_injection_not_duplicated(tmp_path: Path) -> None:
    from hedron.build import run_build
    from hedron.config import HedronSettings

    components = tmp_path / "components" / "X"
    components.mkdir(parents=True)
    (components / "styles.css").write_text(".root { color: red; }\n", encoding="utf-8")
    settings = HedronSettings(
        component_roots=("components",),
        build_dir=".hedron/build",
        theme="default",
        plugins=(),
    )
    built = run_build(project_dir=tmp_path, settings=settings, production=True)
    app = Hedron(
        title="assets",
        security="standard",
        explorer="off",
        session_secret="secret",
        build_dir=built.build_dir,
    )

    @app.page("/")
    def home() -> Page:
        return Page(Text("hi"), title="T")

    with TestClient(app) as client:
        response = client.get("/")
        assert response.text.count('rel="stylesheet"') == 2
        assert response.text.count("hedron-default.css") == 1
        assert response.text.count("/hedron-assets/") >= 1
        assert response.text.index("hedron-default.css") < response.text.index("/hedron-assets/")
        assert response.text.count("hedron-disclose.mjs") == 1
        assert getattr(app.state, "hedron_build_manifest", None) is not None
        assert app.state.hedron_build_manifest.assets.assets


def test_mount_build_assets_replaces_different_tree(tmp_path: Path) -> None:
    a = tmp_path / "a" / "assets"
    b = tmp_path / "b" / "assets"
    a.mkdir(parents=True)
    b.mkdir(parents=True)
    (a / "a.txt").write_text("A", encoding="utf-8")
    (b / "b.txt").write_text("B", encoding="utf-8")
    app = FastAPI()
    mount_build_assets(app, tmp_path / "a")
    mount_build_assets(app, tmp_path / "b")
    assert Path(app.state.hedron_assets_dir).resolve() == b.resolve()
    with TestClient(app) as client:
        assert client.get("/hedron-assets/b.txt").status_code == 200
        assert client.get("/hedron-assets/a.txt").status_code == 404


def test_browser_only_folder_registers_component(tmp_path: Path) -> None:
    reset_registry_for_tests()
    folder = tmp_path / "components" / "Glow"
    folder.mkdir(parents=True)
    (folder / "browser.mjs").write_text("export {}", encoding="utf-8")
    discovered = discover_component_folders([tmp_path / "components"])
    apply_discovery_to_registry(discovered)
    metas = list(get_registry().components())
    assert any(m.name == "Glow" and m.browser_modules for m in metas)


def test_component_discovery_ignores_application_templates(tmp_path: Path) -> None:
    folder = tmp_path / "components" / "Card"
    folder.mkdir(parents=True)
    (folder / "template.html").write_text(
        "<div>Jinja belongs to the app loader</div>", encoding="utf-8"
    )

    assert discover_component_folders([tmp_path / "components"]) == ()


def test_cli_empty_registry_hints(capsys: pytest.CaptureFixture[str]) -> None:
    from hedron.cli import main

    reset_registry_for_tests()
    with pytest.raises(SystemExit) as routes_exc:
        main(["routes"])
    assert routes_exc.value.code == 0
    err = capsys.readouterr().err
    assert "--app" in err
    with pytest.raises(SystemExit) as components_exc:
        main(["components"])
    assert components_exc.value.code == 0
    err = capsys.readouterr().err
    assert "--app" in err


def test_cli_eject_ignores_registry_folder_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``meta.folder_path`` must not become the eject write root."""
    from hedron.cli import main
    from hedron_core.registry import register_component

    reset_registry_for_tests()
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "eject-fixture"\nversion = "0.0.0"\n\n[tool.hedron]\n',
        encoding="utf-8",
    )
    outside = tmp_path / "outside-root"
    outside.mkdir()
    register_component(
        logical_id="app:demo.Empty",
        name="Empty",
        module="demo",
        distribution="app",
        folder_path=str(outside),
    )
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as exc:
        main(["eject", "Empty", "--force"])
    assert exc.value.code == 0
    expected = tmp_path / "components" / "Empty"
    assert (expected / "accessibility_contract.json").is_file()
    assert not (outside / "accessibility_contract.json").exists()


def test_cli_eject_nothing_written_exits_nonzero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from hedron.cli import main
    from hedron_core.registry import register_component

    reset_registry_for_tests()
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "eject-fixture"\nversion = "0.0.0"\n\n[tool.hedron]\n',
        encoding="utf-8",
    )
    out = tmp_path / "ejected"
    out.mkdir()
    (out / "styles.css").write_text("y", encoding="utf-8")
    (out / "accessibility_contract.json").write_text("{}", encoding="utf-8")
    register_component(
        logical_id="app:demo.Empty",
        name="Empty",
        module="demo",
        distribution="app",
        folder_path=str(out),
    )
    monkeypatch.chdir(tmp_path)
    # Contract + starters already exist without --force → refuse overwrite.
    with pytest.raises(SystemExit) as exc:
        main(["eject", "Empty", "--out", str(out)])
    assert exc.value.code == 1


def test_disclose_script_contract() -> None:
    script = (
        Path(__file__).resolve().parents[2]
        / "packages"
        / "hedron"
        / "src"
        / "hedron"
        / "static"
        / "hedron-disclose.mjs"
    ).read_text(encoding="utf-8")
    assert "${label}" not in script
    assert "innerHTML" not in script
    assert "textContent = label" in script
    assert "rebind()" in script
    assert "data-hedron-disclose-btn" in script
    assert "data-hedron-disclose-panel" in script


def test_include_component_csrf_on_unsafe_methods() -> None:
    from hedron.routing.router import HedronRouter
    from hedron_core.addressable import addressable

    app = Hedron(title="inc", security="standard", explorer="off", session_secret="secret")
    router = HedronRouter()

    @addressable(methods=("GET", "POST"))
    def piece() -> Text:
        return Text("ok")

    router.include_component(piece, path="/piece")
    app.include_router(router)

    with TestClient(app) as client:
        get_ok = client.get("/piece")
        assert get_ok.status_code == 200
        denied = client.post("/piece")
        assert denied.status_code == 403
        token = client.cookies.get("hedron_csrf")
        assert token
        allowed = client.post("/piece", headers={"X-CSRF-Token": token})
        assert allowed.status_code == 200


def test_redirect_rejects_backslash_and_external_without_policy() -> None:
    from fastapi import HTTPException

    from hedron.htmx import approved_headers
    from hedron.security.redirects import redirect_external, redirect_local

    with pytest.raises(HTTPException):
        redirect_local("/\\evil.example")
    with pytest.raises(HTTPException):
        redirect_local("//evil.example")
    with pytest.raises(ValueError):
        approved_headers(redirect="/\\evil.example")
    with pytest.raises(HTTPException):
        redirect_external("https://example.com/x")  # policy omitted → fail closed
    ok = redirect_local("/home?x=1")
    assert ok.status_code == 303


def test_csrf_secure_cookie_on_https_standard() -> None:
    app = Hedron(title="s", security="standard", explorer="off", session_secret="secret")

    @app.page("/")
    def home() -> Page:
        return Page(Text("hi"), title="T")

    with TestClient(app, base_url="https://test") as client:
        response = client.get("/")
        assert "Secure" in (response.headers.get("set-cookie") or "")


def test_production_disables_development_explorer(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HEDRON_ENV", "production")
    monkeypatch.setattr(
        "hedron_core.production_gate.assert_durable_backends",
        lambda **_kwargs: None,
    )
    with pytest.warns(UserWarning, match="Explorer development mode"):
        app = Hedron(
            title="prod",
            security="standard",
            explorer="development",
            session_secret="production-ok-session-secret-32ch",
            production=True,
        )
    assert app.hedron_explorer_mode == "off"
    paths = [getattr(route, "path", "") for route in app.router.routes]
    assert not any(str(path).startswith("/hedron-explorer") for path in paths)
    monkeypatch.delenv("HEDRON_ENV", raising=False)


def test_plugin_start_failure_rolls_back_registry() -> None:
    from hedron.plugins import load_plugins
    from hedron_core.plugins import PluginCapabilities, PluginMeta, get_explorer_panels
    from hedron_core.registry import get_registry

    reset_registry_for_tests()

    def register(ctx: object) -> None:
        from hedron_core.plugins import PluginContext

        assert isinstance(ctx, PluginContext)

        def boom() -> None:
            raise RuntimeError("start failed")

        ctx.on_startup(boom)
        ctx.register_component(
            logical_id="demo:fail.Widget",
            name="FailWidget",
            module="fail",
            distribution="demo",
        )
        ctx.register_explorer_panel(
            panel_id="fail-panel",
            title="Fail",
        )

    register.PLUGIN_META = PluginMeta(  # type: ignore[attr-defined]
        name="fail",
        version="0.4.0",
        distribution="demo",
        capabilities=PluginCapabilities(python=True, explorer_panels=True),
        hedron_version=">=0.44,<0.45",
    )

    class EP:
        name = "fail"

        def load(self) -> object:
            return register

    loader = load_plugins(entry_points=[EP()])
    assert any(c.name == "FailWidget" for c in get_registry().components())
    assert any(p.panel_id == "fail-panel" for p in get_explorer_panels())
    with pytest.raises(RuntimeError, match="start failed"):
        loader.start()
    assert not any(c.name == "FailWidget" for c in get_registry().components())
    assert not any(p.panel_id == "fail-panel" for p in get_explorer_panels())
