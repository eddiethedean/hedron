---
description: Planned first-class interactive, custom-server, and offline maps for Hedron.
---

# `hedron-maps`

**Status:** Planned for phase 0.47 · **Target:** independent Beta `0.1.0`

Stage 0 contract refined by D-082 against Published in-tree `v0.46.0`. No runtime.

`hedron-maps` will provide a typed map grammar, deterministic compilation, a pinned MapLibre host,
custom raster/vector tile sources, and static/offline basemaps while preserving Hedron's semantic
fallback and application-owned security policy.

The initial Supported inventory is deliberately bounded:

- replaceable OpenStreetMap raster default;
- custom XYZ raster, TileJSON, and MVT/vector sources;
- static georeferenced images, PMTiles, bounded MBTiles, and blank maps;
- markers and bounded GeoJSON/line/polygon/circle/raster overlays;
- safe local styles, exact-origin policy, attribution, and resource manifests;
- typed feature/viewport events through ordinary Hedron commands; and
- no-JavaScript, WebGL-failure, source-failure, and air-gapped behavior.

Leaflet/OpenLayers, deck.gl, WMS/WMTS/WFS, arbitrary projections, drawing, terrain, globe, routing,
geocoding, and offline-region download are not in the initial Supported inventory.

Planning authority: [Maps API](../api/MAPS.md) ·
[RFC-0074](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0074-FIRST-CLASS-MAPS.md) ·
[implementation plan](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/HEDRON_MAPS_047.md).
