"""OFFLINE-047 static / PMTiles / MBTiles / blank / bundle."""

from __future__ import annotations

import sqlite3
from pathlib import Path

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


def test_mbtiles_read_closes_connection(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "tiles.mbtiles"
    with sqlite3.connect(path) as connection:
        connection.execute(
            "CREATE TABLE tiles ("
            "zoom_level INTEGER, tile_column INTEGER, tile_row INTEGER, tile_data BLOB)"
        )
        connection.execute("INSERT INTO tiles VALUES (0, 0, 0, ?)", (b"tile",))

    opened: list[sqlite3.Connection] = []
    real_connect = sqlite3.connect

    def connect(*args: object, **kwargs: object) -> sqlite3.Connection:
        connection = real_connect(*args, **kwargs)
        opened.append(connection)
        return connection

    monkeypatch.setattr("hedron_maps.mbtiles.sqlite3.connect", connect)

    assert read_tile(path, z=0, x=0, y=0) == b"tile"
    assert read_tile(path, z=1, x=0, y=0) is None
    assert len(opened) == 2
    for connection in opened:
        with pytest.raises(sqlite3.ProgrammingError):
            connection.execute("SELECT 1")


def test_mbtiles_read_closes_connection_on_sql_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "invalid.mbtiles"
    path.touch()

    opened: list[sqlite3.Connection] = []
    real_connect = sqlite3.connect

    def connect(*args: object, **kwargs: object) -> sqlite3.Connection:
        connection = real_connect(*args, **kwargs)
        opened.append(connection)
        return connection

    monkeypatch.setattr("hedron_maps.mbtiles.sqlite3.connect", connect)

    with pytest.raises(sqlite3.OperationalError):
        read_tile(path, z=0, x=0, y=0)

    assert len(opened) == 1
    with pytest.raises(sqlite3.ProgrammingError):
        opened[0].execute("SELECT 1")
