"""OFFLINE-047 static / PMTiles / MBTiles / blank / bundle."""

from __future__ import annotations

import pytest

from hedron_core import HedronError
from hedron_maps import (
    SYNTHETIC_ARCHIVE,
    Map,
    MBTiles,
    MBTilesArchive,
    NoBasemap,
    PMTiles,
    StaticImage,
    compile_map,
)
from hedron_maps.mbtiles import read_tile
from hedron_maps.offline import bundle_from_paths, offline_resource_closed
from hedron_maps.spec import AccessibilityDef, MapSpec


def _acc() -> AccessibilityDef:
    return AccessibilityDef(title="Offline", description="Air-gap path")


def test_static_image_and_blank_map() -> None:
    static = compile_map(
        MapSpec(
            basemap=StaticImage(
                src="/assets/maps/campus.webp", bounds=(-1, -1, 1, 1), attribution="GIS"
            ),
            accessibility=_acc(),
        )
    )
    assert static.source_kind == "static-image"
    assert static.origins == ()
    blank = compile_map(MapSpec(basemap=None, accessibility=_acc()))
    assert blank.source_kind == "none"
    via_none = Map(basemap=None, title="Blank", description="No tiles").compile_plan()
    assert via_none.source_kind == "none"
    assert isinstance(NoBasemap().kind, str)


def test_pmtiles_and_bundle_are_local() -> None:
    plan = compile_map(
        MapSpec(
            basemap=PMTiles(
                src="/assets/maps/region.pmtiles",
                style="/assets/maps/style.json",
                attribution="OSM",
            ),
            accessibility=_acc(),
        )
    )
    assert plan.source_kind == "pmtiles"
    assert plan.origins == ()
    bundle = bundle_from_paths(
        archive_or_image="/assets/maps/region.pmtiles",
        style="/assets/maps/style.json",
        attribution="OSM",
        hashes={"region.pmtiles": "sha256:abc"},
    )
    assert offline_resource_closed(bundle)
    remote = bundle_from_paths(
        archive_or_image="https://evil.example/x.pmtiles",
        attribution="x",
        hashes={},
    )
    assert offline_resource_closed(remote) is False


def test_mbtiles_declared_handle_and_synthetic_tile() -> None:
    with pytest.raises(HedronError):
        compile_map(
            MapSpec(
                basemap=MBTiles(archive_id="../etc/passwd", attribution="x"),
                accessibility=_acc(),
            )
        )
    archive = MBTilesArchive(archive_id="synthetic", path=SYNTHETIC_ARCHIVE)
    blob = read_tile(archive.path, z=0, x=0, y=0)
    assert blob is not None and blob[:8] == b"\x89PNG\r\n\x1a\n"
    bundle = archive.to_bundle()
    assert "integer XYZ" in " ".join(bundle.limitations)
    assert all(
        "/" not in str(item) or "hedron-maps" in str(item)
        for item in bundle.projections[0].data.values()
        if isinstance(item, str) or True
    )
