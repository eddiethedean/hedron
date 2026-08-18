"""#277: hedron-chart SVG title/desc IDs must be unique per instance."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "packages/hedron-charts/src/hedron_charts/static/hedron-chart.mjs"


def test_chart_svg_ids_are_instance_scoped() -> None:
    source = MODULE.read_text(encoding="utf-8")
    assert 'title.id = "hc-title"' not in source
    assert 'desc.id = "hc-desc"' not in source
    assert "svgLabelSeq" in source
    assert "-title" in source
    assert "-desc" in source
