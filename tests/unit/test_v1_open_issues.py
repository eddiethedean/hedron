from __future__ import annotations

import pytest

from hedron_core import render, register_first_party_icons
from hedron_core.builtins.layout import PageHeader
from hedron_core.builtins.shell import AppShell, HtmxLink, NavGroup
from hedron_core.builtins.style_scope import StyleScope
from hedron_core.theme import Theme, compatibility_theme_vars
from fastapi_workbench.config import WorkbenchConfig
from fastapi_workbench.resolve import resolve_deployment


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
    output = render(
        StyleScope(
            PageHeader("Title", title_tracking="tight", title_wrap="break"),
            presentation={"PageHeader.title": "display"},
        )
    ).html
    assert 'data-hedron-style-recipe="display"' in output
    assert 'data-hedron-type-tracking="tight"' in output
    shell = render(AppShell(nav="links", body="body", nav_collapse="user")).html
    assert 'data-hedron-nav-collapse="user"' in shell
    assert 'aria-controls="main-panel-nav"' in shell


def test_workbench_full_root_path_preserves_origin() -> None:
    resolved = resolve_deployment(
        WorkbenchConfig(),
        environ={"RS_SERVER_URL": "1", "UVICORN_ROOT_PATH": "https://workbench.example/s/u/p/123/"},
        bound_port=123,
    )
    assert resolved.external_origin == "https://workbench.example"
    assert resolved.browser_mount == "/s/u/p/123"


def test_first_party_icon_pack_is_optional() -> None:
    entries = register_first_party_icons()
    assert len(entries) >= 20
    assert all("currentColor" in entry.svg.value for entry in entries)
