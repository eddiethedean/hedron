"""#363: MapPolicy.remote_requests_permitted must fail-closed."""

from __future__ import annotations

import pytest

from hedron_core import HedronError
from hedron_core.codes import HED_MAP_POLICY_0001
from hedron_maps import MapPolicy, OpenStreetMap, RasterTiles, compile_map
from hedron_maps.proxy import assert_ssrf_safe
from hedron_maps.spec import AccessibilityDef, MapSpec, PMTiles


def test_remote_raster_rejected_when_remote_requests_disabled() -> None:
    with pytest.raises(HedronError) as exc:
        compile_map(
            MapSpec(
                basemap=RasterTiles(
                    url="https://tiles.example.com/{z}/{x}/{y}.png",
                    attribution="x",
                ),
                policy=MapPolicy(
                    allowed_origins=("https://tiles.example.com",),
                    remote_requests_permitted=False,
                ),
                accessibility=AccessibilityDef(title="T", description="D"),
            )
        )
    assert exc.value.diagnostic.code == HED_MAP_POLICY_0001


def test_osm_standard_rejected_when_remote_requests_disabled() -> None:
    with pytest.raises(HedronError) as exc:
        compile_map(
            MapSpec(
                basemap=OpenStreetMap.standard(),
                policy=MapPolicy(remote_requests_permitted=False),
                accessibility=AccessibilityDef(title="T", description="D"),
            )
        )
    assert exc.value.diagnostic.code == HED_MAP_POLICY_0001


def test_local_pmtiles_still_compile_when_remote_disabled() -> None:
    plan = compile_map(
        MapSpec(
            basemap=PMTiles(src="/assets/maps/region.pmtiles", attribution="OSM"),
            policy=MapPolicy(remote_requests_permitted=False),
            accessibility=AccessibilityDef(title="T", description="D"),
        )
    )
    assert plan.origins == ()


def test_proxy_rejects_when_remote_requests_disabled() -> None:
    with pytest.raises(HedronError) as exc:
        assert_ssrf_safe(
            "https://tiles.example/t",
            MapPolicy(
                allowed_origins=("https://tiles.example",),
                remote_requests_permitted=False,
            ),
            resolve_dns=False,
        )
    assert exc.value.diagnostic.code == HED_MAP_POLICY_0001
