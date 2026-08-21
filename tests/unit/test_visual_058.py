"""VISUAL-058 evidence."""

from __future__ import annotations

from hedron import Button, DesignSystem, StyleScope
from hedron_core.diagnostics import DiagnosticSeverity
from hedron_core.rendering import RenderContext, RenderMode, render
from hedron_core.theme import contrast_diagnostics


def test_brand_contrast_diagnostics_ok_for_good_seed() -> None:
    design = DesignSystem.brand("visual", accent="#2f6fed")
    findings = contrast_diagnostics(design.to_theme())
    errors = [item for item in findings if item.severity == DiagnosticSeverity.ERROR]
    assert errors == []
    for item in findings:
        assert item.severity in {
            DiagnosticSeverity.WARNING,
            DiagnosticSeverity.INFORMATION,
        }


def test_render_style_scope_and_button() -> None:
    design = DesignSystem.brand("visual-btn", accent="#2f6fed")
    button = design.apply("primary_action", Button("Save"))
    html = render(
        StyleScope(button, theme=design.name, density="comfortable"),
        context=RenderContext.standalone(),
        mode=RenderMode.FRAGMENT,
    ).html
    assert "data-hedron-style-scope" in html
    assert "Save" in html
    assert "hedron-button" in html or "button" in html.lower()
