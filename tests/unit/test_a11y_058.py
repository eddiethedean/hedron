"""A11Y-058 evidence."""

from __future__ import annotations

from hedron import AppShell, DesignSystem, MainPanel, NavLink, Page, StyleScope, Text
from hedron_core.diagnostics import DiagnosticSeverity
from hedron_core.rendering import RenderContext, RenderMode, render
from hedron_core.theme import contrast_diagnostics, contrast_ratio


def test_page_title_and_landmarks() -> None:
    page = Page(
        AppShell(
            nav=NavLink("Home", "/"),
            body=MainPanel(Text("content")),
            brand=Text("Brand"),
        ),
        title="Accessible Home",
    )
    html = render(page, context=RenderContext.standalone(), mode=RenderMode.PAGE).html
    assert "<title>Accessible Home</title>" in html
    assert "<main" in html
    assert "<nav" in html or "hedron-nav" in html


def test_style_scope_density_and_brand_contrast_pairs() -> None:
    html = render(
        StyleScope(Text("dense"), density="compact"),
        context=RenderContext.standalone(),
        mode=RenderMode.FRAGMENT,
    ).html
    assert 'data-hedron-density="compact"' in html

    design = DesignSystem.brand("a11y", accent="#2f6fed")
    theme = design.to_theme()
    findings = contrast_diagnostics(theme)
    assert all(item.severity != DiagnosticSeverity.ERROR for item in findings)
    accent = theme.tokens["color.accent"]
    on_accent = theme.tokens["color.on-accent"]
    assert contrast_ratio(on_accent, accent) >= 4.5
