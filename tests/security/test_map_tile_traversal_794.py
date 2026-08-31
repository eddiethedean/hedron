"""Regression coverage for map tile path allowlists (#794)."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from hedron_core import HedronError
from hedron_core.builtins.map_geo import Map as CoreMap
from hedron_maps import Map as MapsMap


@pytest.mark.parametrize("map_type", [CoreMap, MapsMap])
@pytest.mark.parametrize(
    "tiles",
    [
        "/tiles/../private/{z}/{x}/{y}.png",
        "/tiles/%2e%2e/private/{z}/{x}/{y}.png",
        "/tiles/%252e%252e/private/{z}/{x}/{y}.png",
        "/tiles\\..\\private/{z}/{x}/{y}.png",
    ],
)
def test_tile_allowlist_rejects_normalized_path_traversal(
    map_type: Callable[..., object], tiles: str
) -> None:
    with pytest.raises(HedronError, match="HED-MAP-0002"):
        map_type(tiles=tiles, tile_allowlist=("/tiles",))
