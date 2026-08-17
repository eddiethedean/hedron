---
status: published
---

# Maps

First-class maps live in independent Beta **`hedron-maps` `0.1.0`** (D-078 / D-082). Install
`hedron[maps]` on the 0.47 train or `hedron-maps>=0.1.0,<0.2`. Core `hedron.Map`
and `sanitize_geojson` from the 0.46 train stay compatible.

`hedron.Map`, `sanitize_geojson`, `MarkerSpec`, and `MAP_VIEWPORT_TRIGGER` stay in
`hedron-core`. `MapInteraction` binds untrusted map events to a registered
`ActionHandle`. `OpenStreetMap.standard()` is the `hedron_maps.Map` default only;
core `Map` keeps no OSM default.

Qualify GeoJSON types: **`hedron_maps.GeoJSONLayer`** is the typed overlay layer.
**`hedron_core.GeoJSONLayer`** remains the sanitizer wrapper around core `Map`.

## Beginner map

```python
from hedron_maps import Map

Map(center=(37.7749, -122.4194), zoom=11, title="Bay Area", description="OSM raster map")
```

The default is the versioned `OpenStreetMap.standard()` raster preset
(`openstreetmap-standard`, attribution `© OpenStreetMap contributors`, `{z}{x}{y}`).
It is replaceable and carries no availability guarantee.

## Custom tiles

```python
from hedron_maps import Map, MapPolicy, RasterTiles

basemap = RasterTiles(
    url="https://maps.example.com/tiles/{z}/{x}/{y}.png",
    attribution="© Example Maps",
    tile_size=256,
    min_zoom=0,
    max_zoom=18,
)

Map(
    title="Custom",
    description="Exact-origin XYZ",
    basemap=basemap,
    policy=MapPolicy(allowed_origins={"https://maps.example.com"}),
)
```

Use `compile_map(spec, policy=...)` for a deterministic redacted `MapPlan`. Plans
contain no credentials. Popup content is Hedron nodes or text, not executable HTML.

See [hedron-maps](../packages/hedron-maps.md), [quickstart](../guides/maps.md),
[custom tiles](../guides/maps-custom-tiles.md), [offline](../guides/maps-offline.md),
[policy](../guides/maps-policy.md), [accessibility](../guides/maps-accessibility.md),
[operations](../guides/maps-operations.md), [migration](../guides/maps-migration.md),
and [troubleshooting](../guides/maps-troubleshooting.md).
