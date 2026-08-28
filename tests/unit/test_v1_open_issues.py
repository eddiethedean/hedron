from __future__ import annotations

import pytest

from fastapi_workbench.config import WorkbenchConfig
from fastapi_workbench.resolve import resolve_deployment
from hedron_core import (
    StyleRecipe,
    ThemeBuilder,
    default_theme,
    emit_theme_css,
    export_theme,
    load_theme_package,
    package_theme,
    register_first_party_icons,
    render,
)
from hedron_core.builtins.content import Heading
from hedron_core.builtins.landmarks import Nav
from hedron_core.builtins.layout import PageHeader
from hedron_core.builtins.shell import AppShell, HtmxLink, NavGroup
from hedron_core.builtins.style_scope import StyleScope
from hedron_core.diagnostics import HedronError
from hedron_core.theme import Theme, compatibility_theme_vars


def test_theme_content_width_is_independent_from_navigation_width() -> None:
    theme = Theme(
        name="t",
        tokens={
            "color.bg": "#fff",
            "color.fg": "#000",
            "color.accent": "#00f",
            "color.focus": "#00f",
            "color.danger": "#f00",
            "color.muted": "#666",
            "font.family": "sans",
            "font.size": "1rem",
            "space.unit": "4px",
            "motion.duration": "0s",
            "focus.ring": "2px solid #00f",
        },
        nav_width="18rem",
        content_width="narrow",
    )
    assert compatibility_theme_vars(theme)["--hedron-default-content-width"] == "52rem"


def test_htmx_link_safe_attrs_and_nav_group_action() -> None:
    html = render(HtmxLink("Open", "/open", attrs={"title": "Open", "data-test": "x"})).html
    assert 'title="Open"' in html and 'data-test="x"' in html
    with pytest.raises(ValueError):
        HtmxLink("Open", "/open", attrs={"onclick": "bad"})
    assert "group-action" in render(NavGroup("Group", "item", action="group-action")).html


def test_page_header_scope_and_shell_contract() -> None:
    display_recipe = StyleRecipe.content(
        "auth-display", measure="wide", effect="display", tracking="tight", wrap="balance"
    )
    output = render(
        StyleScope(
            PageHeader("Title"),
            presentation={"PageHeader.title": "auth-display"},
            recipes=(display_recipe,),
        )
    ).html
    assert 'data-hedron-style-recipe="auth-display"' in output
    assert 'data-hedron-type-measure="wide"' in output
    assert 'data-hedron-type-effect="display"' in output
    assert 'data-hedron-type-tracking="tight"' in output
    assert 'data-hedron-type-wrap="balance"' in output
    assert (
        'data-hedron-style-recipe="display"'
        in render(StyleScope(Heading("Heading"), presentation={"Heading": "display"})).html
    )
    explicit = render(
        StyleScope(
            PageHeader("Title", title_measure="narrow", title_wrap="pretty"),
            presentation={"PageHeader.title": "auth-display"},
            recipes=(display_recipe,),
        )
    ).html
    assert 'data-hedron-type-measure="narrow"' in explicit
    assert 'data-hedron-type-wrap="pretty"' in explicit
    nested = render(
        StyleScope(
            StyleScope(
                PageHeader("Nested"),
                presentation={"PageHeader.title": "auth-display"},
            ),
            recipes=(display_recipe,),
        )
    ).html
    assert 'data-hedron-type-measure="wide"' in nested
    shell = render(AppShell(nav="links", body="body", nav_collapse="user")).html
    assert 'data-hedron-nav-collapse="user"' in shell
    assert 'aria-controls="main-panel-nav"' in shell
    custom = render(
        AppShell(nav=Nav("links", id="custom-nav"), body="body", nav_collapse="user")
    ).html
    assert 'aria-controls="custom-nav"' in custom
    always = render(AppShell(nav="links", body="body", nav_collapse="always")).html
    assert 'data-hedron-nav-collapsed="true"' in always


def test_workbench_full_root_path_preserves_origin() -> None:
    resolved = resolve_deployment(
        WorkbenchConfig(),
        environ={"RS_SERVER_URL": "1", "UVICORN_ROOT_PATH": "https://workbench.example/s/u/p/123/"},
        bound_port=123,
    )
    assert resolved.external_origin == "https://workbench.example"
    assert resolved.browser_mount == "/s/u/p/123"
    ordinary = resolve_deployment(
        WorkbenchConfig(mount="/local"),
        environ={"UVICORN_ROOT_PATH": "https://unexpected.example/local"},
        bound_port=123,
    )
    assert ordinary.external_origin == "http://127.0.0.1:123"


def test_first_party_icon_pack_is_optional() -> None:
    entries = register_first_party_icons()
    assert len(entries) >= 20
    assert all("currentColor" in entry.svg.value for entry in entries)


def test_theme_typography_features_emit_consumable_css() -> None:
    tokens = {
        "color.bg": "#fff",
        "color.fg": "#000",
        "color.accent": "#00f",
        "color.focus": "#00f",
        "color.danger": "#f00",
        "color.muted": "#666",
        "font.family": "sans-serif",
        "font.size": "1rem",
        "space.unit": "4px",
        "motion.duration": "0s",
        "focus.ring": "2px solid #00f",
    }
    theme = default_theme().extend(
        "features",
        content_width="wide",
        typography_features={"tnum": 1},
        typography_role_features={"code": {"zero": 1}, "tabular": {"tnum": 1}},
    )
    css = emit_theme_css(theme)
    assert "font-feature-settings" in css
    assert "font-variant-numeric" in css
    assert "--hedron-font-feature-settings-code" in css
    exported = export_theme(theme).to_dict()["theme"]
    assert exported["content_width"] == "wide"
    assert exported["typography_features"] == {"tnum": 1}
    assert exported["typography_role_features"]["code"] == {"zero": 1}
    spec = ThemeBuilder.from_theme(theme).build()
    restored = load_theme_package(package_theme(spec, licenses=("MIT",))).to_theme()
    assert restored.content_width == "wide"
    assert restored.typography_features == {"tnum": 1}
    assert restored.typography_role_features == {"code": {"zero": 1}, "tabular": {"tnum": 1}}
    with pytest.raises(HedronError):
        Theme(name="bad-features", tokens=tokens, typography_features={"tnum": True})


def test_page_header_supports_editorial_wrap_and_tracking_contract() -> None:
    output = render(
        PageHeader(
            "Localized heading",
            eyebrow="Section",
            description="Long localized description",
            title_wrap="balance",
            description_wrap="pretty",
            description_tracking="loose",
            eyebrow_tracking="wide",
            eyebrow_wrap="normal",
        )
    ).html
    assert 'data-hedron-type-wrap="balance"' in output
    assert 'data-hedron-type-wrap="pretty"' in output
    assert 'data-hedron-type-tracking="loose"' in output
    assert 'data-hedron-type-tracking="wide"' in output
