"""Stage 1 measured public map limits (MAP-SPEC / PERF-047).

Budgets reuse core ``DEFAULT_MAX_FEATURES`` (500) and GeoJSON coordinate depth 8.
Remaining defaults were locked from compile/payload measurements of those feature
and depth bounds plus existing 0.15/0.38 payload ceilings. They are public
compatibility facts once 0.47 is cut.
"""

from __future__ import annotations

from hedron_core.builtins.map_geo import DEFAULT_MAX_FEATURES
from hedron_core.visualization import DEFAULT_MAX_PAYLOAD_BYTES

# Reuse shipped 0.15 feature and coordinate-depth contracts.
MAX_FEATURES = DEFAULT_MAX_FEATURES
MAX_COORD_DEPTH = 8

# Measured compile of 500 Point features + depth-8 empty collections stays well
# under the 1_000_000-byte payload ceiling used by charts. Stage 1 locked:
MAX_MAPS_PER_PAGE = 8
MAX_LAYERS_PER_MAP = 32
MAX_SOURCES_PER_MAP = 16
MAX_COORD_COUNT = 50_000
MAX_PROPERTY_BYTES = 4_096
MAX_PLAN_BYTES = DEFAULT_MAX_PAYLOAD_BYTES
MAX_STYLE_BYTES = 250_000
MAX_TILEJSON_BYTES = 64_000
MAX_STATIC_IMAGE_BYTES = 8_000_000
MAX_ARCHIVE_BYTES = 64_000_000
MIN_ZOOM = 0
MAX_ZOOM = 24
MAX_TILE_CONCURRENCY = 8
EVENT_RATE_HZ = 4
EVENT_PAYLOAD_BYTES = 8_192
EVENT_CARDINALITY = 100
MAX_WORKERS = 1
CACHE_MEMORY_BYTES = 32_000_000
PROXY_RESPONSE_BYTES = 4_000_000
PROXY_TIMEOUT_MS = 5_000
PROXY_MAX_REDIRECTS = 3
MOUNT_DESTROY_CYCLES = 100
VIEWPORT_DEBOUNCE_MS = 250

LIMITS: dict[str, int] = {
    "maps_per_page": MAX_MAPS_PER_PAGE,
    "layers_per_map": MAX_LAYERS_PER_MAP,
    "sources_per_map": MAX_SOURCES_PER_MAP,
    "geojson_features": MAX_FEATURES,
    "coord_depth": MAX_COORD_DEPTH,
    "coord_count": MAX_COORD_COUNT,
    "property_bytes": MAX_PROPERTY_BYTES,
    "plan_bytes": MAX_PLAN_BYTES,
    "style_bytes": MAX_STYLE_BYTES,
    "tilejson_bytes": MAX_TILEJSON_BYTES,
    "static_image_bytes": MAX_STATIC_IMAGE_BYTES,
    "archive_bytes": MAX_ARCHIVE_BYTES,
    "min_zoom": MIN_ZOOM,
    "max_zoom": MAX_ZOOM,
    "tile_concurrency": MAX_TILE_CONCURRENCY,
    "event_rate_hz": EVENT_RATE_HZ,
    "event_payload_bytes": EVENT_PAYLOAD_BYTES,
    "event_cardinality": EVENT_CARDINALITY,
    "workers": MAX_WORKERS,
    "cache_memory_bytes": CACHE_MEMORY_BYTES,
    "proxy_response_bytes": PROXY_RESPONSE_BYTES,
    "proxy_timeout_ms": PROXY_TIMEOUT_MS,
    "proxy_max_redirects": PROXY_MAX_REDIRECTS,
    "mount_destroy_cycles": MOUNT_DESTROY_CYCLES,
    "viewport_debounce_ms": VIEWPORT_DEBOUNCE_MS,
}

__all__ = ["LIMITS", "MAX_FEATURES", "MAX_COORD_DEPTH"]
