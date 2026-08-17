"""PROVIDER-047 OSM / RasterTiles / TileJSON / VectorTiles / MapPolicy."""

from __future__ import annotations

import pytest

from hedron_core import HedronError
from hedron_core.codes import HED_MAP_POLICY_0001, HED_MAP_POLICY_0002, HED_MAP_SOURCE_0001
from hedron_maps import MapPolicy, OpenStreetMap, RasterTiles, TileJSON, VectorTiles, compile_map
from hedron_maps.spec import (
    OSM_STANDARD_ATTRIBUTION,
    OSM_STANDARD_ORIGIN,
    AccessibilityDef,
    MapSpec,
)


def test_osm_standard_preset() -> None:
    osm = OpenStreetMap.standard()
    assert osm.kind == "openstreetmap-standard"
    assert "{z}" in osm.tile_url and "{x}" in osm.tile_url and "{y}" in osm.tile_url
    assert osm.attribution == OSM_STANDARD_ATTRIBUTION
    plan = compile_map(
        MapSpec(basemap=osm, accessibility=AccessibilityDef(title="T", description="D"))
    )
    assert OSM_STANDARD_ORIGIN in plan.origins
    assert any("no availability" in w.lower() or "SLA" in w for w in plan.warnings)


def test_raster_requires_policy_origin() -> None:
    tiles = RasterTiles(
        url="https://maps.example.com/{z}/{x}/{y}.png",
        attribution="© Example",
    )
    with pytest.raises(HedronError) as exc:
        compile_map(
            MapSpec(basemap=tiles, accessibility=AccessibilityDef(title="T", description="D"))
        )
    assert exc.value.diagnostic.code == HED_MAP_POLICY_0001
    plan = compile_map(
        MapSpec(
            basemap=tiles,
            policy=MapPolicy(allowed_origins=("https://maps.example.com",)),
            accessibility=AccessibilityDef(title="T", description="D"),
        )
    )
    assert plan.source_kind == "xyz-raster"
    assert "https://maps.example.com" in plan.origins


def test_custom_osm_tile_url_requires_policy_origin() -> None:
    url = "https://evil.example/{z}/{x}/{y}.png"
    with pytest.raises(HedronError) as exc:
        compile_map(
            MapSpec(
                basemap=OpenStreetMap(tile_url=url, attribution="© OpenStreetMap contributors"),
                accessibility=AccessibilityDef(title="T", description="D"),
            )
        )
    assert exc.value.diagnostic.code == HED_MAP_POLICY_0001
    plan = compile_map(
        MapSpec(
            basemap=OpenStreetMap(tile_url=url, attribution="© OpenStreetMap contributors"),
            policy=MapPolicy(allowed_origins=("https://evil.example",)),
            accessibility=AccessibilityDef(title="T", description="D"),
        )
    )
    assert plan.origins == ("https://evil.example",)


def test_credentials_and_protocol_relative_rejected() -> None:
    with pytest.raises(HedronError) as exc:
        compile_map(
            MapSpec(
                basemap=RasterTiles(
                    url="https://user:pass@maps.example.com/{z}/{x}/{y}.png",
                    attribution="x",
                ),
                policy=MapPolicy(allowed_origins=("https://maps.example.com",)),
                accessibility=AccessibilityDef(title="T", description="D"),
            )
        )
    assert exc.value.diagnostic.code == HED_MAP_POLICY_0002
    with pytest.raises(HedronError) as exc2:
        compile_map(
            MapSpec(
                basemap=RasterTiles(url="//maps.example.com/{z}/{x}/{y}.png", attribution="x"),
                accessibility=AccessibilityDef(title="T", description="D"),
            )
        )
    assert exc2.value.diagnostic.code == HED_MAP_POLICY_0002


def test_unsupported_placeholder_rejected() -> None:
    with pytest.raises(HedronError) as exc:
        compile_map(
            MapSpec(
                basemap=RasterTiles(
                    url="https://maps.example.com/{z}/{x}/{y}/{quadkey}.png",
                    attribution="x",
                ),
                policy=MapPolicy(allowed_origins=("https://maps.example.com",)),
                accessibility=AccessibilityDef(title="T", description="D"),
            )
        )
    assert exc.value.diagnostic.code == HED_MAP_SOURCE_0001


def test_tilejson_and_vector_close_origins() -> None:
    policy = MapPolicy(allowed_origins=("https://tiles.example.com",))
    tj = compile_map(
        MapSpec(
            basemap=TileJSON(
                attribution="© Example",
                document={"tiles": ["https://tiles.example.com/{z}/{x}/{y}.png"]},
            ),
            policy=policy,
            accessibility=AccessibilityDef(title="T", description="D"),
        )
    )
    assert tj.source_kind == "tilejson"
    vt = compile_map(
        MapSpec(
            basemap=VectorTiles(
                url="https://tiles.example.com/{z}/{x}/{y}.pbf",
                attribution="© Example",
            ),
            policy=policy,
            accessibility=AccessibilityDef(title="T", description="D"),
        )
    )
    assert vt.source_kind == "mvt-vector"
