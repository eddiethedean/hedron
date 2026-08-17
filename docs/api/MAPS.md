---
status: planned
---

# Maps

!!! warning "Planned 0.47 contract"

    This is the accepted D-078 / RFC-0074 public contract. No `hedron-maps` runtime or package is
    available until the 0.47 gates are Verified.

Install target (not available until the 0.47 gates are Verified):

- flagship extra `hedron[maps]` on the 0.47 train
- independently versioned `hedron-maps` `>=0.1.0,<0.2`

Do not install either extra on the living 0.46 train.

## Beginner map

```python
from hedron_maps import Map

Map(center=(37.7749, -122.4194), zoom=11)
```

The default is the versioned `OpenStreetMap.standard()` raster preset. It supplies visible
attribution and policy diagnostics. It is replaceable and carries no availability guarantee.

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
    basemap=basemap,
    policy=MapPolicy(allowed_origins={"https://maps.example.com"}),
)
```

Applications do not repeat low-level prefix allowlists: compilation derives resource origins and
checks them structurally against policy. Request-derived URLs and embedded credentials are invalid.

## Offline maps

```python
from hedron_maps import Map, PMTiles, StaticImage

campus = Map(
    basemap=StaticImage(
        src="/assets/maps/campus.webp",
        bounds=(-122.53, 37.69, -122.35, 37.84),
        attribution="City GIS Department",
    )
)

region = Map(
    basemap=PMTiles(
        src="/assets/maps/region.pmtiles",
        style="/assets/maps/region-style.json",
        attribution="© OpenStreetMap contributors",
    )
)

blank = Map(basemap=None, layers=[...], fit="layers")
```

`MBTiles(path=...)` is server-side only and registers through a declared application feature/route;
the path is never accepted from a request. `OfflineMapBundle` validates that archives, styles,
sprites, glyphs, attribution, and hashes form a closed local resource set.

## Planned Supported surface

| Surface | Purpose |
|---|---|
| `Map`, `MapSpec`, `MapPlan`, `compile_map` | Author, validate, and deterministically compile maps |
| `MapPolicy` | Exact egress, local assets, source kinds, bounds, and limits |
| `OpenStreetMap` | Maintained standard preset with attribution/policy metadata |
| `RasterTiles`, `TileJSON`, `VectorTiles` | Custom raster and MVT/vector infrastructure |
| `StaticImage`, `PMTiles`, `MBTiles` | No-external-service and air-gapped basemaps |
| `MapStyle`, `MapTheme` | Safe style subset and Hedron presentation tokens |
| `ViewState`, `Bounds` | Initial camera, fit, bounds, padding, and zoom constraints |
| `MarkerLayer`, `GeoJSONLayer`, `LineLayer`, `PolygonLayer`, `CircleLayer`, `RasterLayer` | Initial closed layer inventory |
| typed map events | Untrusted feature/viewport inputs mapped to ordinary commands |
| `OfflineMapBundle` | Validate and package a closed local map asset set |

## Renderer and fallback

The enhanced renderer is a pinned local strict-CSP MapLibre host. MapLibre classes, options,
callbacks, and arbitrary style expressions are not public Hedron APIs. Every map renders a useful
semantic title, description, attribution, and feature/action alternative before enhancement.

## Existing `hedron.Map`

`from hedron import Map` remains the core policy-bounded presentation component. Existing
`tiles`/`tile_allowlist`, markers, and GeoJSON calls remain valid. `hedron_maps.Map` is additive and
compiles to the compatible semantic boundary.

See [RFC-0074](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0074-FIRST-CLASS-MAPS.md)
and the [implementation plan](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/HEDRON_MAPS_047.md).
