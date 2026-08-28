# Map operations

- Pin `hedron-maps>=0.1.3,<0.2` with the coordinated 1.0 artifacts. Until publication,
  public PyPI applications should use `hedron[maps]>=0.66.2,<0.67`.
- Vendor MapLibre 5.6.1 (strict CSP + worker). Do not load a CDN runtime.
- Explorer: `/hedron-explorer/maps` inspects origins, CSP, attribution, limits, and
  events without executing untrusted map data.
- MBTiles routes: `/hedron-maps/mbtiles/{archive_id}/{z}/{x}/{y}` after
  `app.include(MBTilesArchive(...))`.
- Limits are public facts in `MapPlan.limits` (maps/page, layers, features, zoom, tiles,
  events, proxy, mount/destroy).
- Zero MapLibre bytes when `hedron-maps` is not installed.
