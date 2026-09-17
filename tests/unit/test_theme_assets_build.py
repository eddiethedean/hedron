"""Theme, assets, config, and build tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from hedron.config import load_hedron_settings
from hedron_core import (
    HedronError,
    Theme,
    aurora_theme,
    classic_theme,
    default_theme,
    emit_theme_css,
    ensure_builtin_themes_registered,
    folio_theme,
    get_registry,
)
from hedron_core.assets import fingerprint_bytes
from hedron_core.manifests import AssetManifest, BuildManifest
from hedron_core.theme import REQUIRED_A11Y_TOKENS


def _run_production_build(project_dir: str) -> None:
    from hedron.build import run_build
    from hedron.config import HedronSettings

    run_build(
        project_dir=Path(project_dir),
        settings=HedronSettings(build_dir=".hedron/build", theme="default", plugins=()),
        production=True,
    )


def test_default_theme_has_a11y_tokens() -> None:
    theme = default_theme()
    for token in REQUIRED_A11Y_TOKENS:
        assert token in theme.tokens
    css = emit_theme_css(theme)
    assert "@layer tokens" in css
    assert "--hedron-color-bg" in css
    assert "prefers-color-scheme: dark" in css
    assert "prefers-reduced-motion" in css


def test_aurora_is_a_registered_first_party_theme() -> None:
    themes = ensure_builtin_themes_registered()
    assert [theme.name for theme in themes] == ["folio", "classic", "aurora"]
    assert get_registry().get_theme("aurora") is not None
    assert "#6d3ce7" in emit_theme_css(aurora_theme())


def test_classic_preserves_legacy_default_palette_and_registration() -> None:
    ensure_builtin_themes_registered()
    classic = classic_theme()
    legacy = default_theme()
    assert classic.name == "classic"
    assert legacy.name == "default"
    assert classic.tokens == legacy.tokens
    assert classic.modes == legacy.modes
    assert classic.tokens["color.accent"] == "#2563eb"
    assert get_registry().get_theme("classic").tokens == get_registry().get_theme("default").tokens


def test_folio_default_accent_preserves_green_palette() -> None:
    original = folio_theme()
    for accent in ("green", " GREEN ", "#17675e"):
        selected = folio_theme(accent=accent)
        assert selected == original
    assert original.tokens["color.accent"] == "#17675e"
    assert original.modes["dark"]["color.accent"] == "#8ed3be"


@pytest.mark.parametrize(
    "accent", ["blue", "violet", "amber", "rose", "#f00", "#00f", "#fff", "#000", "#f0e123"]
)
def test_folio_accent_preserves_surfaces_and_readable_color_pairs(accent: str) -> None:
    from hedron_core.theme import contrast_ratio

    base = folio_theme()
    selected = folio_theme(accent=accent)
    assert selected.name.startswith("folio-")
    assert selected.parent == "folio"
    assert selected.tokens["color.accent"] != base.tokens["color.accent"]
    for mode in ("light", "dark"):
        original = {**base.tokens, **base.modes.get(mode, {})}
        colors = {**selected.tokens, **selected.modes.get(mode, {})}
        for key in (
            "color.bg",
            "color.surface",
            "color.surface-muted",
            "color.fg",
            "color.muted",
            "color.border",
            "color.success",
            "color.warning",
            "color.danger",
            "font.display",
            "shape.radius",
            "elevation.raised",
        ):
            assert colors[key] == original[key]
        assert contrast_ratio(colors["color.accent"], colors["color.on-accent"]) >= 4.5
        assert contrast_ratio(colors["color.accent"], colors["color.bg"]) >= 4.5
        assert contrast_ratio(colors["color.accent"], colors["color.accent-soft"]) >= 4.5
        assert colors["color.focus"] == colors["chart.focus"] == colors["color.accent"]
        assert colors["focus.ring"] == f"3px solid {colors['color.accent']}"


def test_folio_hex_accent_is_canonical_and_rejects_invalid_values() -> None:
    assert folio_theme(accent="#ABC") == folio_theme(accent="#aabbcc")
    with pytest.raises(HedronError):
        folio_theme(accent="unknown")
    with pytest.raises(HedronError):
        folio_theme(accent="red; background: url(example)")


def test_folio_app_accents_are_isolated_and_available_through_edron() -> None:
    import edron as ed
    from hedron import Hedron

    blue = Hedron(accent="blue", session_secret="test-secret")
    rose = Hedron(accent="rose", session_secret="test-secret")
    green = Hedron(session_secret="test-secret")
    edron = ed.App(title="Folio accents", accent="violet", session_secret="test-secret")
    assert blue.hedron_theme == "folio-blue"
    assert rose.hedron_theme == "folio-rose"
    assert green.hedron_theme == "folio"
    assert edron.native.hedron_theme == "folio-violet"
    for theme in ("classic", "default", "aurora"):
        with pytest.raises(ValueError, match="Folio|folio"):
            Hedron(theme=theme, accent="blue", session_secret="test-secret")


@pytest.mark.parametrize("accent", ["blue", "rose", "#00f"])
def test_folio_accent_page_loads_its_local_stylesheet(accent: str) -> None:
    from fastapi.testclient import TestClient

    from hedron import Hedron, Page, Text

    app = Hedron(accent=accent, session_secret="test-secret")

    @app.page("/")
    def home():
        return Page(Text("Accent preview"))

    theme = folio_theme(accent=accent)
    path = f"/hedron-static/folio-accent/{theme.name.removeprefix('folio-')}.css"
    with TestClient(app) as client:
        html = client.get("/")
        assert html.status_code == 200
        assert f'href="{path}"' in html.text
        css = client.get(path)
        assert css.status_code == 200
        assert css.headers["content-type"].startswith("text/css")
        assert f"--hedron-color-accent: {theme.tokens['color.accent']};" in css.text
        assert client.get("/hedron-static/folio-accent/invalid.css").status_code == 404


def test_folio_accent_assets_are_available_in_flask_and_django() -> None:
    from types import ModuleType

    from django.test import Client, override_settings
    from flask import Flask

    from hedron_django.static_mount import hedron_static_urlpatterns
    from hedron_flask.static_mount import mount_hedron_static

    app = Flask(__name__)
    mount_hedron_static(app)
    response = app.test_client().get("/hedron-static/folio-accent/blue.css")
    assert response.status_code == 200
    assert "--hedron-color-bg: #191a1b;" in response.text
    expected_css = response.text
    assert app.test_client().get("/hedron-static/folio-accent/invalid.css").status_code == 404
    urls = ModuleType("folio_accent_urls")
    urls.urlpatterns = hedron_static_urlpatterns()
    with override_settings(ROOT_URLCONF=urls):
        response = Client().get("/hedron-static/folio-accent/blue.css")
        assert response.status_code == 200
        assert response.content.decode() == expected_css
        assert Client().get("/hedron-static/folio-accent/invalid.css").status_code == 404


def test_folio_accent_configuration_and_production_build(tmp_path: Path) -> None:
    from hedron.build import run_build
    from hedron.config import settings_digest

    config = tmp_path / "pyproject.toml"
    config.write_text('[tool.hedron]\ntheme = "folio"\naccent = "blue"\nplugins = []\n')
    settings = load_hedron_settings(config)
    assert settings.accent == "blue"
    green_settings = load_hedron_settings(config, overrides={"accent": "green"})
    assert settings_digest(settings) != settings_digest(green_settings)
    result = run_build(project_dir=tmp_path, settings=settings, production=True)
    assert result.css_bundle_path is not None
    css = result.css_bundle_path.read_text(encoding="utf-8")
    blue = folio_theme(accent="blue")
    assert f"--hedron-color-accent: {blue.tokens['color.accent']};" in css
    assert f"--hedron-color-accent: {blue.modes['dark']['color.accent']};" in css
    assert "--hedron-color-bg: #191a1b;" in css
    assert '[data-hedron-theme="folio-blue"]' in css


@pytest.mark.parametrize("accent", [False, "invalid", "#12"])
def test_folio_accent_configuration_rejects_invalid_choices(tmp_path: Path, accent: object) -> None:
    (tmp_path / "pyproject.toml").write_text("[tool.hedron]\n")
    with pytest.raises(HedronError):
        load_hedron_settings(tmp_path, overrides={"accent": accent})
    with pytest.raises(HedronError, match="Accent requires Folio"):
        load_hedron_settings(tmp_path, overrides={"theme": "classic", "accent": "blue"})


@pytest.mark.parametrize("choice", [None, "folio", "classic", "default"])
def test_automatic_theme_and_explicit_legacy_choices(tmp_path: Path, choice: str | None) -> None:
    from hedron import Hedron
    from hedron.config import HedronSettings
    from hedron_core import resolve_theme_preference

    config = tmp_path / "pyproject.toml"
    config.write_text(
        "[tool.hedron]\n" + (f'theme = "{choice}"\n' if choice else ""), encoding="utf-8"
    )
    expected = choice or "folio"
    assert load_hedron_settings(config).theme == expected
    assert HedronSettings().theme == "folio"
    app = Hedron(theme=choice) if choice else Hedron()
    assert app.hedron_theme == expected
    preference = resolve_theme_preference(choice, "light")
    assert preference.theme == ("classic" if choice == "default" else expected)


@pytest.mark.parametrize(
    ("choice", "accent"), [("folio", "#17675e"), ("classic", "#2563eb"), ("default", "#2563eb")]
)
def test_production_build_preserves_named_theme(tmp_path: Path, choice: str, accent: str) -> None:
    from hedron.build import run_build
    from hedron.config import HedronSettings

    result = run_build(
        project_dir=tmp_path,
        settings=HedronSettings(theme=choice, plugins=()),
        production=True,
    )
    assert result.css_bundle_path is not None
    css = result.css_bundle_path.read_text(encoding="utf-8")
    assert f"--hedron-color-accent: {accent};" in css
    if choice == "folio":
        assert "--hedron-shape-radius: 0.3rem;" in css
        assert "--hedron-font-display: Georgia" in css


def test_production_build_accepts_aurora_theme(tmp_path: Path) -> None:
    from hedron.build import run_build
    from hedron.config import HedronSettings

    result = run_build(
        project_dir=tmp_path,
        settings=HedronSettings(
            build_dir=".hedron/build",
            theme="aurora",
            plugins=(),
        ),
        production=True,
    )
    assert result.css_bundle_path is not None
    css = result.css_bundle_path.read_text(encoding="utf-8")
    assert "#6d3ce7" in css
    assert "#c4a7ff" in css


def _relative_luminance(hex_color: str) -> float:
    channels = [int(hex_color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast_ratio(first: str, second: str) -> float:
    lighter, darker = sorted(
        (_relative_luminance(first), _relative_luminance(second)), reverse=True
    )
    return (lighter + 0.05) / (darker + 0.05)


@pytest.mark.parametrize(
    "theme",
    [default_theme(), classic_theme(), aurora_theme(), folio_theme()],
    ids=lambda item: item.name,
)
def test_builtin_theme_light_and_dark_pairs_meet_aa_contrast(theme: Theme) -> None:
    light = theme.tokens
    dark = {**theme.tokens, **theme.modes["dark"]}

    for palette in (light, dark):
        assert _contrast_ratio(palette["color.bg"], palette["color.fg"]) >= 4.5
        assert _contrast_ratio(palette["color.bg"], palette["color.muted"]) >= 4.5
        assert _contrast_ratio(palette["color.accent"], palette["color.on-accent"]) >= 4.5
        assert _contrast_ratio(palette["color.danger"], palette["color.on-danger"]) >= 4.5
        for tone in ("success", "warning", "danger", "accent"):
            assert _contrast_ratio(palette[f"color.{tone}"], palette[f"color.{tone}-soft"]) >= 4.5
        for surface in ("surface", "surface-muted", "accent-soft"):
            assert _contrast_ratio(palette["color.muted"], palette[f"color.{surface}"]) >= 4.5
        assert _contrast_ratio(palette["color.selection-bg"], palette["color.selection-fg"]) >= 4.5


def test_default_stylesheet_is_local_layered_and_customizable() -> None:
    stylesheet = (
        Path(__file__).resolve().parents[2]
        / "packages"
        / "hedron"
        / "src"
        / "hedron"
        / "static"
        / "hedron-default.css"
    ).read_text(encoding="utf-8")

    assert (
        "@layer reset, tokens, base, components, application, utilities, overrides;" in stylesheet
    )
    assert ".hedron-card" in stylesheet
    assert ".hedron-form-field" in stylesheet
    assert ".hedron-dialog" in stylesheet
    assert ".hedron-chat-input" in stylesheet
    assert ".hedron-app-shell" in stylesheet
    assert ".hedron-toggle-switch" in stylesheet
    assert ".hedron-timeline" in stylesheet
    assert ".hedron-gallery" in stylesheet
    assert ':root[data-hedron-theme="aurora"]' in stylesheet
    assert "--hedron-aurora-glow" in stylesheet
    assert "--hedron-default-on-accent" in stylesheet
    assert "var(--hedron-gap" in stylesheet
    assert "data-hedron-gap" in stylesheet or "--hedron-gap" in stylesheet
    assert "\n  table {" in stylesheet
    assert ".hedron-chart-fallback" in stylesheet
    assert "prefers-color-scheme: dark" in stylesheet
    assert "http://" not in stylesheet
    assert "https://" not in stylesheet
    assert "url(" not in stylesheet


def test_default_stylesheet_copies_stay_in_sync() -> None:
    root = Path(__file__).resolve().parents[2] / "packages"
    core = root / "hedron-core" / "src" / "hedron_core" / "static" / "hedron-default.css"
    facade = root / "hedron" / "src" / "hedron" / "static" / "hedron-default.css"
    assert core.read_bytes() == facade.read_bytes()


def test_theme_missing_token_rejected() -> None:
    with pytest.raises(HedronError) as exc:
        Theme(name="bad", tokens={"color.bg": "#fff"})
    assert exc.value.diagnostic.code == "HED-THEME-0002"


def test_config_unknown_key(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[project]\nname="x"\nversion="0"\n[tool.hedron]\nnope=1\n',
        encoding="utf-8",
    )
    with pytest.raises(HedronError) as exc:
        load_hedron_settings(pyproject)
    assert exc.value.diagnostic.code == "HED-CONFIG-0001"


def test_config_load_defaults(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[tool.hedron]\nformat_version = 1\ncomponent_roots = ["components"]\ntheme = "default"\n',
        encoding="utf-8",
    )
    settings = load_hedron_settings(pyproject)
    assert settings.component_roots == ("components",)
    assert settings.theme == "default"


def test_fingerprint_deterministic(tmp_path: Path) -> None:
    out = tmp_path / "assets"
    a = fingerprint_bytes(
        b"hello",
        output_dir=out,
        logical_id="x",
        kind="css",
        filename_prefix="components",
        suffix=".css",
        content_type="text/css",
    )
    b = fingerprint_bytes(
        b"hello",
        output_dir=out,
        logical_id="x",
        kind="css",
        filename_prefix="components",
        suffix=".css",
        content_type="text/css",
    )
    assert a.path == b.path
    assert a.digest == b.digest


def test_build_with_component_folder(tmp_path: Path) -> None:
    from hedron.build import run_build
    from hedron.config import HedronSettings

    components = tmp_path / "components" / "StatusPill"
    components.mkdir(parents=True)
    (components / "badge.png").write_bytes(b"png-bytes")
    (components / "styles.css").write_text(
        ".root { color: green; background: url(badge.png); }\n.title { font-weight: 600; }\n",
        encoding="utf-8",
    )
    (components / "component.py").write_text(
        "from hedron_core import Component, Props, Field, html\n"
        "\n"
        "class StatusPillProps(Props):\n"
        "    label: str = Field(default='ok')\n"
        "\n"
        "class StatusPill(Component[StatusPillProps]):\n"
        "    props_type = StatusPillProps\n"
        "    def render(self):\n"
        "        return html.div(self.props.label, class_='root')\n",
        encoding="utf-8",
    )
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        "[tool.hedron]\nformat_version = 1\n"
        'component_roots = ["components"]\n'
        'build_dir = ".hedron/build"\n',
        encoding="utf-8",
    )
    settings = HedronSettings(
        component_roots=("components",),
        build_dir=".hedron/build",
        theme="default",
        plugins=(),
    )
    first = run_build(project_dir=tmp_path, settings=settings, production=True)
    second = run_build(project_dir=tmp_path, settings=settings, production=True)
    assert first.manifest.to_dict()["digest"] == second.manifest.to_dict()["digest"]
    assert first.css_bundle_path is not None
    assert first.css_bundle_path.is_file()
    css = first.css_bundle_path.read_text(encoding="utf-8")
    assert "@layer tokens" in css
    assert "@layer components" in css
    assert "/hedron-assets/" in css
    assert "url(" in css
    # Authored relative name rewritten to fingerprinted path.
    assert "badge.png)" not in css.replace(" ", "")
    BuildManifest.from_dict(first.manifest.to_dict()).validate_format()
    AssetManifest.from_dict(first.manifest.assets.to_dict()).validate_format()


def test_build_temp_staging_same_device(tmp_path: Path) -> None:
    """Staging directory must live under the build parent (same filesystem)."""
    from hedron.build import run_build
    from hedron.config import HedronSettings

    components = tmp_path / "components" / "X"
    components.mkdir(parents=True)
    (components / "styles.css").write_text(".root { color: blue; }\n", encoding="utf-8")
    settings = HedronSettings(
        component_roots=("components",),
        build_dir="out/build",
        theme="default",
        plugins=(),
    )
    result = run_build(project_dir=tmp_path, settings=settings, production=True)
    assert result.build_dir == (tmp_path / "out" / "build").resolve()
    assert (result.build_dir / "manifest.json").is_file()
    # No leftover staging dirs after successful promote.
    leftovers = list((tmp_path / "out").glob(".hedron-build-tmp-*"))
    assert leftovers == []


def test_concurrent_builds_share_a_project_scoped_lock(tmp_path: Path) -> None:
    """Concurrent builds cannot interleave registry mutations or promotion (#101)."""
    from concurrent.futures import ThreadPoolExecutor

    from hedron.build import run_build
    from hedron.config import HedronSettings

    settings = HedronSettings(build_dir=".hedron/build", theme="default", plugins=())
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(
            executor.map(
                lambda _: run_build(project_dir=tmp_path, settings=settings, production=True),
                range(8),
            )
        )

    build_dir = tmp_path / ".hedron" / "build"
    assert all(result.build_dir == build_dir for result in results)
    assert (build_dir / "manifest.json").is_file()
    assert list(build_dir.parent.glob(".hedron-build-tmp-*")) == []
    assert list(build_dir.parent.glob(".hedron-build-bak-*")) == []


def test_concurrent_process_builds_share_a_project_scoped_lock(tmp_path: Path) -> None:
    """The filesystem lock also serializes separate production workers (#101)."""
    from multiprocessing import get_context

    workers = [
        get_context("spawn").Process(target=_run_production_build, args=(str(tmp_path),))
        for _ in range(4)
    ]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(timeout=30)
        assert worker.exitcode == 0

    build_dir = tmp_path / ".hedron" / "build"
    assert (build_dir / "manifest.json").is_file()
    assert list(build_dir.parent.glob(".hedron-build-tmp-*")) == []
    assert list(build_dir.parent.glob(".hedron-build-bak-*")) == []


def test_strict_csp_no_unsafe_inline_styles() -> None:
    from hedron.security.policy import SecurityPolicy

    policy = SecurityPolicy.from_name("strict")
    csp = policy.content_security_policy or ""
    assert "style-src 'self'" in csp
    assert "unsafe-inline" not in csp


def test_disclose_script_avoids_label_innerhtml_interpolation() -> None:
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


def test_data_editor_enhancement_marks_fallback_upgraded() -> None:
    script = (
        Path(__file__).resolve().parents[2]
        / "packages"
        / "hedron-data"
        / "src"
        / "hedron_data"
        / "assets"
        / "tabulator"
        / "editor.js"
    ).read_text(encoding="utf-8")
    assert ":scope > .hedron-data-editor-fallback" in script
    assert 'fallback.setAttribute("data-hedron-fallback", "upgraded")' in script
    assert 'fallback.setAttribute("aria-hidden", "true")' in script
    assert 'delBtn.className = "hedron-button hedron-button-danger"' in script
    assert 'ev.key === "Escape"' in script
    assert 'td.dataset.editCancel = "1"' in script
    assert 'if (td.dataset.editCancel === "1")' in script
    assert "res.status === 403" in script
    assert "await res.json()" in script
    # 403 path must not call res.json() before the status check.
    forbidden_idx = script.index("res.status === 403")
    json_idx = script.index("await res.json()", forbidden_idx)
    assert forbidden_idx < json_idx
    assert "function sanitizeFormulaCell" in script
    assert "function buildCsv" in script
    assert "JSON.stringify(row[c.field]" not in script
    assert "function reconcileAfterSuccess" in script
    assert "snapshotSaveBatch" in script
