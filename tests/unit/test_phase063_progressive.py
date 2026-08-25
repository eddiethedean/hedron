"""Executable evidence for the formerly progressive phase 0.63 contracts."""

from __future__ import annotations

from pathlib import Path

import pytest
from tests.unit.charts_038_helpers import sample_spec

from hedron_charts.compile import compile_chart
from hedron_charts.export import export_svg
from hedron_core import (
    compare_style_bundle_sizes,
    compile_style_bundle,
    emit_visualization_theme_css,
    html,
    react_island_host,
    react_island_recipe,
    render,
    resolve_visualization_theme,
    style_bundle_asset_refs,
)


def test_bundle_is_deterministic_smaller_and_dependency_ordered() -> None:
    first = compile_style_bundle(components=("button", "card"))
    second = compile_style_bundle(components=("card", "button"))
    assert first.css == second.css
    assert first.digest == second.digest
    assert compare_style_bundle_sizes()["selected_is_smaller"] is True
    refs = style_bundle_asset_refs(("card", "button"))
    assert [ref.href.rsplit("/", 1)[-1] for ref in refs] == [
        "tokens.css",
        "base.css",
        "a11y.css",
        "button.css",
        "card.css",
    ]
    static = Path(__file__).parents[2] / "packages/hedron-core/src/hedron_core/static/bundles"
    assert all((static / ref.href.rsplit("/", 1)[-1]).is_file() for ref in refs)


def test_visualization_palette_has_shared_roles_and_non_color_encodings() -> None:
    palette = resolve_visualization_theme(series_count=4)
    assert {item.role for item in palette.series} == {
        "series-1",
        "series-2",
        "series-3",
        "series-4",
    }
    assert all(item.pattern and item.marker for item in palette.series)
    forced = resolve_visualization_theme(accessibility_mode="forced-colors", series_count=2)
    printed = resolve_visualization_theme(accessibility_mode="print", series_count=2)
    assert forced.roles["selection"] == "Highlight"
    assert printed.roles["surface"] == "#ffffff"
    css = emit_visualization_theme_css()
    assert "--hedron-chart-series-1" in css
    assert "prefers-reduced-transparency" in css


def test_chart_plan_and_svg_use_semantic_visualization_roles() -> None:
    plan = compile_chart(sample_spec())
    assert "chart.series-1" in plan.theme.tokens
    assert "chart.pattern.series-1" in plan.theme.tokens
    assert "var(--hedron-chart-series-1" in export_svg(plan)


def test_react_island_recipe_is_pinned_and_fallback_safe() -> None:
    recipe = react_island_recipe()
    assert recipe.maturity == "Experimental"
    assert recipe.version == "18.3.1"
    assert recipe.ssr_fallback is True
    assert recipe.csp_safe is True
    assert recipe.cleanup is True
    rendered = render(
        react_island_host("chart", html.span("Accessible fallback"), props={"series": 1})
    ).html
    assert "Accessible fallback" in rendered
    assert 'data-hedron-react-island="legacy-chart-island"' in rendered
    assert 'data-hedron-react-ssr-fallback="true"' in rendered


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_react_island_rejects_non_finite_props(value: float) -> None:
    with pytest.raises(ValueError, match="finite JSON-serializable"):
        react_island_host("chart", html.span("Accessible fallback"), props={"value": value})
