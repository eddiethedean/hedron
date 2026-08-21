"""LAYOUT-057 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron_core import Grid, GridItem, Text
from hedron_core.rendering import RenderContext, RenderMode, render


def test_layout_057_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.57.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["LAYOUT-057"]["state"] == "Verified"


def test_grid_tracks_and_item_spans() -> None:
    ctx = RenderContext.standalone()
    html = render(
        Grid(
            GridItem(Text("wide"), span=2),
            GridItem(Text("narrow"), span=1),
            columns={"base": 1, "md": 3},
            tracks={"base": "default", "md": "wide"},
            gap="sm",
        ),
        context=ctx,
        mode=RenderMode.FRAGMENT,
    ).html
    assert 'data-hedron-layout="grid"' in html
    assert 'data-hedron-columns="1"' in html
    assert 'data-hedron-columns-md="3"' in html
    assert 'data-hedron-track="default"' in html
    assert 'data-hedron-track-md="wide"' in html
    assert 'data-hedron-span="2"' in html
    assert "hedron-grid-item" in html
    # Spans must not invent CSS order that reorders DOM.
    assert "order:" not in html


def test_grid_default_omits_track_marker() -> None:
    ctx = RenderContext.standalone()
    html = render(Grid(Text("a"), columns=3), context=ctx, mode=RenderMode.FRAGMENT).html
    assert 'data-hedron-columns="3"' in html
    assert "data-hedron-track=" not in html


def test_stylesheet_has_responsive_grid_selectors() -> None:
    css = Path("packages/hedron-core/src/hedron_core/static/hedron-default.css").read_text(
        encoding="utf-8"
    )
    assert '.hedron-grid[data-hedron-columns-md="3"]' in css
    assert '.hedron-grid-item[data-hedron-span-md="2"]' in css
    assert '.hedron-grid[data-hedron-track="default"]:not([data-hedron-columns])' in css
