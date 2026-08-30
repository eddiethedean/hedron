"""Phase 0.15 M5 Map / GeoJSON (RFC-0033)."""

from __future__ import annotations

import html as html_lib
import json
import math
import re

import pytest

from hedron_core import HedronError, Map, MarkerSpec, RenderMode, render
from hedron_core.codes import HED_MAP_0001, HED_MAP_0002, HED_MAP_0003


def test_map_renders_table_alternative_with_markers() -> None:
    node = Map(
        center=(37.77, -122.42),
        zoom=12,
        markers=[
            MarkerSpec(id="ferry", lat=37.7955, lon=-122.3937, label="Ferry Building"),
            {"id": "park", "lat": 37.7694, "lon": -122.4862, "label": "Golden Gate Park"},
        ],
        mark="city-map",
    )
    html = render(node, mode=RenderMode.FRAGMENT).html
    assert 'data-hedron-mark="city-map"' in html
    assert 'class="hedron-map"' in html
    assert "hedron-map-alternative" in html
    assert "Ferry Building" in html
    assert "Golden Gate Park" in html
    assert "37.7955" in html
    assert "-122.3937" in html
    assert 'data-hedron-map="true"' in html
    assert "Map features and markers" in html


def test_map_rejects_oversized_geojson_feature_count() -> None:
    features = [
        {
            "type": "Feature",
            "properties": {"name": f"f{i}"},
            "geometry": {"type": "Point", "coordinates": [0.0, 0.0]},
        }
        for i in range(3)
    ]
    with pytest.raises(HedronError) as exc:
        Map(
            center=(0.0, 0.0),
            geojson={"type": "FeatureCollection", "features": features},
            max_features=2,
        )
    assert exc.value.diagnostic.code == HED_MAP_0001


def test_map_rejects_disallowed_tile_prefix() -> None:
    with pytest.raises(HedronError) as exc:
        Map(
            center=(0.0, 0.0),
            tiles="https://evil.example/tiles/{z}/{x}/{y}.png",
            tile_allowlist=("/assets/tiles/",),
        )
    assert exc.value.diagnostic.code == HED_MAP_0002

    allowed = Map(
        center=(0.0, 0.0),
        tiles="/assets/tiles/{z}/{x}/{y}.png",
        tile_allowlist=("/assets/tiles/", "https://tiles.example/"),
    )
    html = render(allowed, mode=RenderMode.FRAGMENT).html
    assert 'data-tiles="/assets/tiles/{z}/{x}/{y}.png"' in html


def test_map_rejects_empty_and_host_prefix_bypass_allowlist() -> None:
    with pytest.raises(HedronError) as exc_empty:
        Map(
            center=(0.0, 0.0),
            tiles="https://evil.example/tiles/{z}/{x}/{y}.png",
            tile_allowlist=("",),
        )
    assert exc_empty.value.diagnostic.code == HED_MAP_0002

    with pytest.raises(HedronError) as exc_bypass:
        Map(
            center=(0.0, 0.0),
            tiles="https://tiles.example.evil.com/x/{z}/{x}/{y}.png",
            tile_allowlist=("https://tiles.example",),
        )
    assert exc_bypass.value.diagnostic.code == HED_MAP_0002

    ok = Map(
        center=(0.0, 0.0),
        tiles="https://tiles.example/x/{z}/{x}/{y}.png",
        tile_allowlist=("https://tiles.example",),
    )
    html = render(ok, mode=RenderMode.FRAGMENT).html
    assert "https://tiles.example/x/" in html


def test_malicious_geojson_properties_do_not_become_script_tags() -> None:
    node = Map(
        center=(1.0, 2.0),
        geojson={
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Safe Place",
                        "html": "<script>alert(1)</script>",
                        "onclick": "evil()",
                        "description": "<script>document.cookie</script>",
                    },
                    "geometry": {"type": "Point", "coordinates": [2.0, 1.0]},
                }
            ],
        },
    )
    html = render(node, mode=RenderMode.FRAGMENT).html
    assert "<script>" not in html
    assert "Safe Place" in html
    # Escaped text may remain; executable tags must not.
    assert "</script>" not in html or "&lt;/script&gt;" in html or "&lt;script" in html
    assert 'data-geojson="' in html
    assert "onclick" not in html.lower() or "&quot;onclick&quot;" not in html
    # Dangerous keys stripped from payload.
    assert '"html"' not in html
    assert "alert(1)" not in html or "&lt;script&gt;" in html


@pytest.mark.parametrize("feature_id", [math.nan, math.inf, -math.inf, True])
def test_map_rejects_non_json_geojson_feature_ids(feature_id: object) -> None:
    with pytest.raises(HedronError) as excinfo:
        Map(
            geojson={
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "id": feature_id,
                        "properties": {"name": "invalid id"},
                        "geometry": {"type": "Point", "coordinates": [0, 0]},
                    }
                ],
            }
        )
    assert excinfo.value.diagnostic.code == HED_MAP_0003


def test_map_geojson_attribute_is_strict_browser_json() -> None:
    node = Map(
        geojson={
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": "place-1",
                    "properties": {"name": "Place"},
                    "geometry": {"type": "Point", "coordinates": [2, 1]},
                }
            ],
        }
    )
    markup = render(node, mode=RenderMode.FRAGMENT).html
    match = re.search(r'data-geojson="([^"]*)"', markup)
    assert match is not None
    payload = html_lib.unescape(match.group(1))
    assert json.loads(payload)["features"][0]["id"] == "place-1"


def test_map_strips_non_finite_values_from_nested_property_arrays() -> None:
    node = Map(
        geojson={
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": "place-1",
                    "properties": {"values": [1, math.nan, [math.inf, 2]]},
                    "geometry": None,
                }
            ],
        }
    )
    markup = render(node, mode=RenderMode.FRAGMENT).html
    match = re.search(r'data-geojson="([^"]*)"', markup)
    assert match is not None
    payload = json.loads(html_lib.unescape(match.group(1)))
    assert payload["features"][0]["properties"]["values"] == [1, [2]]
