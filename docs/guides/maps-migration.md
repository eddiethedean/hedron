# Migrate core Map to hedron-maps

Core `from hedron import Map` keeps `center, zoom, tiles, tile_allowlist, markers, geojson`.
That path never silently becomes MapLibre.

To migrate explicitly:

```python
from hedron_maps import Map, MapPolicy, RasterTiles

Map(
    title="Migrated",
    description="Same semantic table",
    basemap=RasterTiles(url=tiles, attribution=attribution),
    policy=MapPolicy(allowed_origins={origin}),
    markers=markers,
    geojson=geojson,
)
```

Optional compatibility constructor `tiles=` / `tile_allowlist=` on `hedron_maps.Map`
compiles to the same fallback; it is never a silent remote MapLibre mount.

Uninstall `hedron-maps` and revert the import to leave no maps routes, assets, workers,
or projections.
