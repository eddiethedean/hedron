"""hedron-maps: first-class maps, offline geospatial presentation, and typed events."""

from __future__ import annotations

from hedron_maps.compile import compile_map, parse_map_spec
from hedron_maps.element import TAG_NAME, Map
from hedron_maps.interaction import (
    FeatureActivated,
    FeatureSelected,
    LayerVisibilityChanged,
    MapFailed,
    MapInteraction,
    MapLoaded,
    ViewportChanged,
)
from hedron_maps.mbtiles import MBTilesArchive
from hedron_maps.offline import SYNTHETIC_ARCHIVE, bundle_from_paths
from hedron_maps.pins import MAPLIBRE_VERSION, RUNTIME_PINS, assert_pins_present, verify_pin
from hedron_maps.spec import (
    Bounds,
    CircleLayer,
    GeoJSONLayer,
    LineLayer,
    MapPlan,
    MapPolicy,
    MapSpec,
    MapStyle,
    MapTheme,
    MarkerLayer,
    MBTiles,
    NoBasemap,
    OfflineMapBundle,
    OpenStreetMap,
    PMTiles,
    PolygonLayer,
    RasterLayer,
    RasterTiles,
    StaticImage,
    TileJSON,
    VectorTiles,
    ViewState,
)

__version__ = "1.0.6"

__all__ = [
    "MAPLIBRE_VERSION",
    "RUNTIME_PINS",
    "SYNTHETIC_ARCHIVE",
    "Bounds",
    "CircleLayer",
    "FeatureActivated",
    "FeatureSelected",
    "GeoJSONLayer",
    "LayerVisibilityChanged",
    "LineLayer",
    "MBTiles",
    "MBTilesArchive",
    "Map",
    "MapFailed",
    "MapInteraction",
    "MapLoaded",
    "MapPlan",
    "MapPolicy",
    "MapSpec",
    "MapStyle",
    "MapTheme",
    "MarkerLayer",
    "NoBasemap",
    "OfflineMapBundle",
    "OpenStreetMap",
    "PMTiles",
    "PolygonLayer",
    "RasterLayer",
    "RasterTiles",
    "StaticImage",
    "TAG_NAME",
    "TileJSON",
    "VectorTiles",
    "ViewState",
    "ViewportChanged",
    "__version__",
    "assert_pins_present",
    "bundle_from_paths",
    "compile_map",
    "parse_map_spec",
    "verify_pin",
]
