"""ECOSYSTEM-054: phase 0.54 chrome companions (#523–#537, RFC-0081).

Covers the wave 1 layout/chrome/theme primitives and the wave 2 icon,
typography, palette, appearance, overlay, state, and table surfaces.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from hedron_core import (
    ActionGroup,
    AppShell,
    Badge,
    Button,
    Card,
    DescriptionList,
    FlowStep,
    FormGrid,
    Icon,
    Link,
    Page,
    PageHeader,
    ProcessFlow,
    RequestIndicator,
    SkipLink,
    SplitView,
    Stack,
    StateView,
    Table,
    TableColumn,
    Text,
    Theme,
    Typography,
    compile_palette,
    contrast_diagnostics,
    contrast_ratio,
    default_theme,
    design_system_vars,
    emit_theme_css,
    render,
)
from hedron_core.builtins.appearance import (
    APPEARANCES,
    DENSITIES,
    EMPHASES,
    SIZES,
    STATE_KINDS,
    TYPOGRAPHY_ROLES,
    appearance_data,
    normalize_responsive_int,
)
from hedron_core.diagnostics import HedronError
from hedron_core.icons import register_icon
from hedron_core.registry import get_registry
from hedron_core.theme import OVERLAY_ELEVATION_TOKENS

ROOT = Path(__file__).resolve().parents[2]
STYLESHEETS = (
    ROOT / "packages/hedron-core/src/hedron_core/static/hedron-default.css",
    ROOT / "packages/hedron/src/hedron/static/hedron-default.css",
)


@pytest.fixture
def chrome_icon() -> str:
    register_icon(
        "test-chrome-054",
        '<svg viewBox="0 0 16 16"><path d="M2 8h12"/></svg>',
        title="Chrome test icon",
        source="tests/unit/test_ecosystem_054",
    )
    return "test-chrome-054"


def test_wave1_and_wave2_components_are_registered() -> None:
    names = {meta.name for meta in get_registry().components()}
    expected = {
        "ActionGroup",
        "FlowStep",
        "FormGrid",
        "Icon",
        "PageHeader",
        "ProcessFlow",
        "RequestIndicator",
        "SkipLink",
        "SplitView",
        "StateView",
        "Typography",
    }
    assert expected <= names


def test_page_with_appshell_chrome_renders_every_slot(chrome_icon: str) -> None:
    page = Page(
        SkipLink("#main-panel"),
        AppShell(
            banner=Text("Read-only maintenance window"),
            brand=Text("Data Mover", role="title"),
            env_badge=Text("staging", role="label"),
            account=RequestIndicator("Working…", id="global-indicator"),
            nav_groups={
                "Operate": [Link("Pipelines", "/", class_="hedron-nav-link")],
                "Administer": [Link("Settings", "/settings", class_="hedron-nav-link")],
            },
            nav_footer=Text("v0.54"),
            app_footer=Text("Hedron owns the stylesheet"),
            content_width="wide",
            body=Stack(
                PageHeader(
                    "Pipelines",
                    eyebrow="Operate",
                    description="Move and verify datasets.",
                    actions=ActionGroup(
                        Button("New pipeline", leading_icon=chrome_icon),
                        align="end",
                        label="Pipeline actions",
                    ),
                ),
                SplitView(
                    Card(
                        ProcessFlow(
                            FlowStep("Stage", status="complete"),
                            FlowStep("Transform", status="current"),
                            FlowStep("Publish", status="blocked"),
                            label="Migration pipeline",
                        )
                    ),
                    StateView("Awaiting approval", kind="permission"),
                    ratio="2:1",
                ),
                FormGrid(Text("field"), columns={"base": 1, "md": 2}),
            ),
        ),
        title="Chrome",
    )
    html = render(page).html

    assert 'class="hedron-skip-link"' in html
    assert 'href="#main-panel"' in html
    assert 'data-hedron-app-shell-header="true"' in html
    assert 'class="hedron-app-shell-banner"' in html
    assert 'class="hedron-app-shell-brand"' in html
    assert 'data-hedron-app-env="true"' in html
    assert 'class="hedron-app-shell-account"' in html
    assert 'data-hedron-nav-group="true"' in html
    assert 'aria-label="Operate"' in html
    assert 'class="hedron-app-shell-nav-footer"' in html
    assert 'data-hedron-app-footer="true"' in html
    assert 'data-hedron-content-width="wide"' in html
    assert 'data-hedron-page-header="true"' in html
    assert 'data-hedron-split-ratio="2-1"' in html
    assert 'data-hedron-columns="1"' in html and 'data-hedron-columns-md="2"' in html
    assert 'data-hedron-process-flow="true"' in html
    assert 'data-hedron-flow-status="current"' in html
    assert 'data-hedron-state-view="permission"' in html
    assert f'data-hedron-icon="{chrome_icon}"' in html


def test_appshell_without_chrome_keeps_the_legacy_markup() -> None:
    html = render(Page(AppShell(nav=[Link("Home", "/")], body=Text("body")))).html
    assert 'class="hedron-app-shell-nav"' in html
    assert 'class="hedron-main-panel"' in html
    assert "hedron-app-shell-header" not in html
    assert "hedron-app-shell-banner" not in html
    assert "hedron-app-shell-footer" not in html


def test_appshell_rejects_unknown_content_width() -> None:
    with pytest.raises(HedronError):
        AppShell(content_width="enormous")


def test_split_view_and_action_group_vocabularies_are_closed() -> None:
    with pytest.raises(HedronError):
        SplitView(Text("a"), Text("b"), ratio="7:9")
    with pytest.raises(HedronError):
        ActionGroup(align="sideways")


def test_responsive_columns_normalize_and_validate() -> None:
    assert normalize_responsive_int(2, label="columns") == {"base": 2}
    assert normalize_responsive_int({"md": 3}, label="columns") == {"base": 3, "md": 3}
    with pytest.raises(HedronError):
        normalize_responsive_int({"xxl": 2}, label="columns")
    with pytest.raises(HedronError):
        FormGrid(columns=9)


def test_shared_appearance_vocabulary_matches_the_locked_contract() -> None:
    assert SIZES == ("sm", "md", "lg")
    assert DENSITIES == ("compact", "comfortable", "spacious")
    assert APPEARANCES == ("solid", "outline", "soft", "ghost")
    assert EMPHASES == ("primary", "secondary", "danger", "neutral")
    assert STATE_KINDS == ("loading", "empty", "error", "permission", "offline", "success")
    assert appearance_data(size="sm", density="compact") == {
        "hedron-size": "sm",
        "hedron-density": "compact",
    }
    with pytest.raises(HedronError):
        appearance_data(emphasis="loud")


def test_typography_roles_emit_class_and_data_hooks() -> None:
    html = render(
        Page(
            Text("eyebrow", role="eyebrow", as_="span"),
            Typography("Title", role="title"),
        )
    ).html
    assert 'class="hedron-text hedron-type-eyebrow"' in html
    assert 'data-hedron-type-role="eyebrow"' in html
    assert 'class="hedron-text hedron-type-title"' in html
    assert set(TYPOGRAPHY_ROLES) == {
        "display",
        "eyebrow",
        "title",
        "body",
        "label",
        "caption",
        "mono",
    }
    with pytest.raises(HedronError):
        Text("x", role="shouty")


def test_icon_requires_a_registered_name_and_sizes(chrome_icon: str) -> None:
    html = render(Page(Icon(chrome_icon, size="lg"))).html
    assert 'data-hedron-size="lg"' in html
    assert 'role="img"' in html
    assert "<svg" in html
    with pytest.raises(HedronError):
        Icon("never-registered-054")


def test_table_columns_density_and_sticky_are_optional() -> None:
    plain = render(Page(Table(["A"], [["1"]]))).html
    assert "hedron-table" not in plain

    rich = render(
        Page(
            Table(
                rows=[["nightly", Badge("Running", tone="info"), "1284"]],
                columns=[
                    TableColumn(header="Run", size="wide"),
                    TableColumn(header="Status"),
                    TableColumn(header="Rows", numeric=True),
                ],
                density="compact",
                sticky_header=True,
                zebra=True,
            )
        )
    ).html
    assert 'class="hedron-table-scroll"' in rich
    assert 'data-hedron-density="compact"' in rich
    assert 'data-hedron-sticky-header="true"' in rich
    assert 'data-hedron-zebra="true"' in rich
    assert 'data-hedron-numeric="true"' in rich
    assert 'data-hedron-col-size="wide"' in rich
    assert "<th" in rich and "Run" in rich


def test_table_rejects_mismatched_column_metadata() -> None:
    with pytest.raises(ValueError):
        Table(["A", "B"], [], columns=[TableColumn(header="A")])


def test_description_list_presentation_props_are_additive() -> None:
    plain = render(Page(DescriptionList(("Term", Text("Value"))))).html
    assert "hedron-description-list" not in plain

    rich = render(Page(DescriptionList(("Term", Text("Value")), columns=2, density="compact"))).html
    assert 'class="hedron-description-list"' in rich
    assert 'data-hedron-columns="2"' in rich
    assert 'data-hedron-density="compact"' in rich


def test_theme_design_system_fields_emit_css_variables() -> None:
    theme = default_theme().extend(
        "chrome054",
        palette={"brand.seed": "#2f6fed"},
        density="comfortable",
        shape={"radius": "0.65rem"},
        nav_width="16rem",
        elevation={"raised": "0 1px 2px rgb(15 23 42 / 8%)"},
    )
    assert theme.parent == "default"

    variables = design_system_vars(theme)
    assert variables["--hedron-theme-name"] == "chrome054"
    assert variables["--hedron-theme-parent"] == "default"
    assert variables["--hedron-palette-brand-seed"] == "#2f6fed"
    assert variables["--hedron-density"] == "comfortable"
    assert variables["--hedron-shape-radius"] == "0.65rem"
    assert variables["--hedron-nav-width"] == "16rem"
    assert variables["--hedron-elevation-raised"].startswith("0 1px 2px")

    css = emit_theme_css(theme)
    for name in variables:
        assert f"{name}:" in css
    # Overlay/stacking tokens ship with every theme so overlays need no app CSS.
    for token in OVERLAY_ELEVATION_TOKENS:
        assert f"--hedron-{token}:" in css
    assert '[data-hedron-theme="chrome054"]' in css


def test_theme_elevation_can_override_overlay_tokens() -> None:
    theme = default_theme().extend("overlay054", elevation={"layer-overlay": "4200"})
    variables = design_system_vars(theme)
    assert variables["--hedron-layer-overlay"] == "4200"
    assert "--hedron-elevation-layer-overlay" not in variables


def test_theme_rejects_unsafe_design_system_values() -> None:
    with pytest.raises(HedronError):
        default_theme().extend("bad054", shape={"radius": "1rem; color: red"})
    with pytest.raises(HedronError):
        default_theme().extend("bad054b", density="airy")
    with pytest.raises(HedronError):
        default_theme().extend("bad054c", nav_width="wide")


def test_theme_extend_merges_without_mutating_the_parent() -> None:
    base = default_theme()
    derived = base.extend("derived054", tokens={"color.accent": "#123456"})
    assert derived.tokens["color.accent"] == "#123456"
    assert base.tokens["color.accent"] != "#123456"
    assert derived.modes["dark"]["color.bg"] == base.modes["dark"]["color.bg"]


def test_compile_palette_is_deterministic_and_meets_aa() -> None:
    first = compile_palette("#2f6fed")
    assert first == compile_palette("#2f6fed")
    assert contrast_ratio(first["color.fg"], first["color.bg"]) >= 4.5
    assert contrast_ratio(first["color.on-accent"], first["color.accent"]) >= 4.5
    assert contrast_diagnostics(first) == []
    with pytest.raises(HedronError):
        compile_palette("not-a-color")


def test_contrast_diagnostics_flag_a_failing_pair() -> None:
    tokens = dict(default_theme().tokens)
    tokens["color.fg"] = "#f2f4f8"
    theme = Theme(name="lowcontrast054", tokens=tokens)
    findings = contrast_diagnostics(theme)
    assert findings
    assert any(item.code == "HED-THEME-0007" for item in findings)
    assert any("color.fg" in item.explanation for item in findings)


def test_default_stylesheet_ships_the_new_class_hooks() -> None:
    core, facade = (path.read_text(encoding="utf-8") for path in STYLESHEETS)
    assert core == facade
    for hook in (
        ".hedron-page-header",
        ".hedron-split",
        ".hedron-form-grid",
        ".hedron-action-group",
        ".hedron-skip-link",
        ".hedron-request-indicator",
        ".hedron-process-flow",
        ".hedron-state-view",
        ".hedron-icon",
        ".hedron-nav-group",
        ".hedron-app-shell-header",
        ".hedron-type-eyebrow",
        ".hedron-visually-hidden",
        "--hedron-nav-width",
    ):
        assert hook in core, hook
    assert "url(" not in core
    assert "http://" not in core and "https://" not in core
