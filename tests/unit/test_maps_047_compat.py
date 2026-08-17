"""COMPAT-047 / REGRESS-047 upgrade fixtures 1-7."""

from __future__ import annotations

from pathlib import Path

from hedron_core import Map as CoreMap
from hedron_core import MarkerSpec, RenderMode, render
from hedron_maps import MAPLIBRE_VERSION, Map, MapPolicy, RasterTiles
from hedron_maps.pins import pin_facts


def test_fixture_1_core_map_without_maps_symbols() -> None:
    src = Path("packages/hedron-core/src/hedron_core/builtins/map_geo.py").read_text(
        encoding="utf-8"
    )
    assert "hedron_maps" not in src
    node = CoreMap(
        center=(37.77, -122.42),
        zoom=12,
        tiles="/assets/tiles/{z}/{x}/{y}.png",
        tile_allowlist=("/assets/tiles/",),
        markers=[MarkerSpec(id="ferry", lat=37.7955, lon=-122.3937, label="Ferry Building")],
        geojson={
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"name": "Park"},
                    "geometry": {"type": "Point", "coordinates": [-122.48, 37.76]},
                }
            ],
        },
    )
    html = render(node, mode=RenderMode.FRAGMENT).html
    assert "hedron-map-alternative" in html
    assert "Ferry Building" in html
    assert "hedron-map " in html or 'class="hedron-map"' in html


def test_fixture_2_explicit_migrate_to_raster_and_policy() -> None:
    plan = Map(
        center=(0.0, 0.0),
        title="Migrated",
        description="RasterTiles",
        basemap=RasterTiles(
            url="https://maps.example.com/{z}/{x}/{y}.png", attribution="© Example"
        ),
        policy=MapPolicy(allowed_origins=("https://maps.example.com",)),
        markers=[{"id": "a", "lat": 1.0, "lon": 2.0, "label": "A"}],
    ).compile_plan()
    assert plan.source_kind == "xyz-raster"
    assert "© Example" in plan.attribution


def test_fixture_3_osm_then_custom_xyz() -> None:
    osm = Map(center=(0.0, 0.0), title="OSM", description="Default").compile_plan()
    custom = Map(
        center=(0.0, 0.0),
        title="XYZ",
        description="Custom",
        basemap=RasterTiles(
            url="https://maps.example.com/{z}/{x}/{y}.png", attribution="© Example"
        ),
        policy=MapPolicy(allowed_origins=("https://maps.example.com",)),
    ).compile_plan()
    assert osm.preset_id == "openstreetmap-standard"
    assert custom.preset_id is None
    assert custom.source_kind == "xyz-raster"


def test_fixture_4_network_denied_pmtiles() -> None:
    from hedron_maps import PMTiles

    plan = Map(
        title="Air gap",
        description="Local",
        basemap=PMTiles(src="/assets/maps/region.pmtiles", attribution="local"),
    ).compile_plan()
    assert plan.origins == ()
    assert all(not item.startswith("https://") for item in plan.resources)


def test_fixture_5_core_does_not_register_maps_assets() -> None:
    import hedron_core
    from hedron_core.registry import get_registry, reset_registry_for_tests

    reset_registry_for_tests()
    hedron_core._register_builtins()
    assets = [item.logical_id for item in get_registry().assets()]
    assert not any(item.startswith("hedron-maps:") for item in assets)


def test_fixture_6_missing_plan_still_has_semantics() -> None:
    html = render(Map(title="Skew", description="Fallback remains"), mode=RenderMode.FRAGMENT).html
    assert "hedron-map-alternative" in html
    assert "Fallback remains" in html


def test_fixture_7_charts_maplibre_stays_explicit() -> None:
    facts = pin_facts()
    assert facts["inherits_charts_pin"] is False
    assert facts["version"] == MAPLIBRE_VERSION
    assert facts["charts_maplibre_pin"] == "4.5.0"
    charts = Path("packages/hedron-charts/src/hedron_charts/pins.py").read_text(encoding="utf-8")
    assert '"4.5.0"' in charts
