"""VISUAL-038 tokens and gallery states."""

from __future__ import annotations

from tests.unit.charts_038_helpers import sample_plan, sample_spec

from hedron_charts.assets_038 import chart_css_path
from hedron_charts.compile import compile_chart

REQUIRED_TOKENS = (
    "--hedron-chart-color-1",
    "--hedron-chart-axis",
    "--hedron-chart-grid",
    "--hedron-chart-label",
    "--hedron-chart-font",
    "--hedron-chart-focus-ring",
    "--hedron-chart-tooltip-bg",
    "--hedron-chart-empty",
    "--hedron-chart-density-compact",
)


def test_public_tokens_present() -> None:
    css = chart_css_path().read_text(encoding="utf-8")
    for token in REQUIRED_TOKENS:
        assert token in css
    assert "prefers-color-scheme: dark" in css
    assert "forced-colors: active" in css
    assert "prefers-reduced-motion: reduce" in css
    assert "@media print" in css


def test_theme_modes_compile() -> None:
    for mode in ("light", "dark", "forced-colors", "print"):
        raw = sample_spec().to_json_dict()
        raw["theme"] = {**raw.get("theme", {}), "mode": mode}
        plan = compile_chart(raw)
        assert plan.theme.mode == mode


def test_adversarial_labels_do_not_break_compile() -> None:
    from tests.unit.charts_038_helpers import sample_rows

    plan = sample_plan(data=sample_rows("adversarial"), kind="bar")
    assert plan.mark_count == 2
