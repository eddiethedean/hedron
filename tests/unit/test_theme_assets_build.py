"""Theme, assets, config, and build tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from hedron.config import load_hedron_settings
from hedron_core import HedronError, Theme, default_theme, emit_theme_css
from hedron_core.assets import fingerprint_bytes
from hedron_core.manifests import AssetManifest, BuildManifest
from hedron_core.theme import REQUIRED_A11Y_TOKENS


def test_default_theme_has_a11y_tokens() -> None:
    theme = default_theme()
    for token in REQUIRED_A11Y_TOKENS:
        assert token in theme.tokens
    css = emit_theme_css(theme)
    assert "@layer tokens" in css
    assert "--hedron-color-bg" in css
    assert "prefers-color-scheme: dark" in css
    assert "prefers-reduced-motion" in css


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
    (components / "template.hdx").write_text(
        '<div class="root"><span class="title">{label}</span></div>\n',
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
    (components / "template.hdx").write_text('<div class="root">{label}</div>\n', encoding="utf-8")
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
