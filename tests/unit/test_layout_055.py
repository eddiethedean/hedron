"""LAYOUT-055 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron import MasterDetail, Text, render
from hedron_core.rendering import RenderMode


def test_layout_055_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.55.toml").read_text(encoding="utf-8"))
    assert gate["evidence"][1]["id"] == "LAYOUT-055"


def test_issue_544_master_detail_named_regions_and_states() -> None:
    md = MasterDetail(Text("list"), Text("detail"), master_id="master", detail_id="detail")
    assert md.fragment_regions() == ("master", "detail")
    html = render(md, mode=RenderMode.FRAGMENT).html
    assert 'id="master"' in html
    assert 'id="detail"' in html
    assert 'data-hedron-layout="master-detail"' in html

    empty = MasterDetail(Text("list"), state="empty", empty_message="Pick one")
    empty_html = render(empty, mode=RenderMode.FRAGMENT).html
    assert "Pick one" in empty_html
