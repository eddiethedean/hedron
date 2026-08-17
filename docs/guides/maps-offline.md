# Offline maps: static, PMTiles, MBTiles, air-gap

Four first-class offline paths:

```python
from hedron_maps import MBTiles, Map, PMTiles, StaticImage

campus = Map(
    title="Campus",
    description="Static image",
    basemap=StaticImage(src="/assets/maps/campus.webp", bounds=(-122.53, 37.69, -122.35, 37.84), attribution="GIS"),
)
region = Map(
    title="Region",
    description="PMTiles",
    basemap=PMTiles(src="/assets/maps/region.pmtiles", style="/assets/maps/style.json", attribution="OSM"),
)
```

`MBTiles` is a declared `archive_id` plus a construction-time path via
`MBTilesArchive` / `Hedron.include_feature`. Integer XYZ routes are owned by the
flagship/adapters. Never pass a filesystem path from a request.

`basemap=None` is a valid blank map. Air-gap: every resource must be same-origin;
undeclared `https://` origins fail compile. Package data includes a synthetic test
archive. Hedron does not prefetch public OSM for offline use.
