"""#358: TileJSON / PMTiles / MBTiles must compile MapLibre sources."""

from __future__ import annotations

from hedron_maps import MapPolicy, MBTiles, PMTiles, TileJSON, compile_map
from hedron_maps.spec import AccessibilityDef, MapSpec, StaticImage


def _acc() -> AccessibilityDef:
    return AccessibilityDef(title="T", description="D")


def test_tilejson_document_tiles_become_style_sources() -> None:
    plan = compile_map(
        MapSpec(
            basemap=TileJSON(
                attribution="© Example",
                document={"tiles": ["https://tiles.example.com/{z}/{x}/{y}.png"]},
            ),
            policy=MapPolicy(allowed_origins=("https://tiles.example.com",)),
            accessibility=_acc(),
        )
    )
    assert "basemap" in plan.style["sources"]
    assert plan.style["sources"]["basemap"]["tiles"] == [
        "https://tiles.example.com/{z}/{x}/{y}.png"
    ]
    assert any(layer.get("source") == "basemap" for layer in plan.style["layers"])


def test_pmtiles_and_mbtiles_emit_basemap_source() -> None:
    pm = compile_map(
        MapSpec(
            basemap=PMTiles(src="/assets/maps/region.pmtiles", attribution="OSM"),
            accessibility=_acc(),
        )
    )
    assert pm.style["sources"]["basemap"]["url"] == "/assets/maps/region.pmtiles"
    mb = compile_map(
        MapSpec(
            basemap=MBTiles(archive_id="synthetic", attribution="x"),
            accessibility=_acc(),
        )
    )
    tiles = mb.style["sources"]["basemap"]["tiles"]
    assert "/hedron-maps/mbtiles/synthetic/{z}/{x}/{y}" in tiles


def test_static_image_emits_image_source() -> None:
    plan = compile_map(
        MapSpec(
            basemap=StaticImage(src="/assets/maps/campus.webp", attribution="GIS"),
            accessibility=_acc(),
        )
    )
    assert plan.style["sources"]["basemap"]["type"] == "image"
    assert plan.style["sources"]["basemap"]["url"] == "/assets/maps/campus.webp"
