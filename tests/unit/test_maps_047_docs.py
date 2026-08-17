"""DOCS-047 / packet tracking for 0.47."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from _gate_047 import TRACKING_ISSUE  # noqa: E402


def test_tracking_issue_bound() -> None:
    assert TRACKING_ISSUE == "#350"
    packet = (ROOT / "docs/acceptance/RELEASE_0_47.md").read_text(encoding="utf-8")
    assert TRACKING_ISSUE in packet
    status = (ROOT / "docs/STATUS.md").read_text(encoding="utf-8")
    assert TRACKING_ISSUE in status
    roadmap = (ROOT / "docs/ROADMAP.md").read_text(encoding="utf-8")
    assert TRACKING_ISSUE in roadmap
    trace = (ROOT / "docs/TRACEABILITY.md").read_text(encoding="utf-8")
    assert TRACKING_ISSUE in trace


def test_docs_qualify_geojson_layer_and_maps_guides() -> None:
    maps_api = (ROOT / "docs/api/MAPS.md").read_text(encoding="utf-8")
    pkg = (ROOT / "docs/packages/hedron-maps.md").read_text(encoding="utf-8")
    impl = (ROOT / "docs/implementation/HEDRON_MAPS_047.md").read_text(encoding="utf-8")
    assert "hedron_maps.GeoJSONLayer" in maps_api
    assert "hedron_core" in maps_api and "GeoJSONLayer" in maps_api
    assert "0.1.0" in pkg
    assert "maps/page" in impl or "maps_per_page" in impl
    for rel in (
        "docs/guides/maps.md",
        "docs/guides/maps-custom-tiles.md",
        "docs/guides/maps-offline.md",
        "docs/guides/maps-policy.md",
        "docs/guides/maps-accessibility.md",
        "docs/guides/maps-operations.md",
        "docs/guides/maps-migration.md",
        "docs/guides/maps-troubleshooting.md",
        "docs/guides/whats-new-0.47.md",
    ):
        assert (ROOT / rel).is_file(), rel
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "hedron" in text.lower()
