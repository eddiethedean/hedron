---
description: Independent Beta first-class maps for Hedron.
---

# `hedron-maps`

**Package maturity:** Beta · **Package version:** `0.1.0` (phase 0.47) · extra `hedron[maps]`  
Living Hedron train `0.60.x` (in-tree tip and PyPI release `v0.60.2`; PyPI flagship pins use
`>=0.60.2,<0.61` ).

`hedron-maps` provides an explicit map grammar, deterministic compilation, a pinned MapLibre
5.6.1 strict-CSP host, custom raster/vector tile sources, and static/offline basemaps
while preserving Hedron's semantic fallback and application-owned security policy.

The Supported inventory is deliberately bounded:

- replaceable OpenStreetMap raster default on `hedron_maps.Map` only;
- custom XYZ raster, TileJSON, and MVT/vector sources;
- static georeferenced images, PMTiles, bounded MBTiles, and blank maps;
- markers and bounded GeoJSON/line/polygon/circle/raster overlays;
- `hedron_maps.GeoJSONLayer` overlays vs `hedron_core.GeoJSONLayer` sanitizer;
- safe local styles, exact-origin policy, attribution, and resource manifests;
- feature/viewport events through ordinary Hedron commands; and
- no-JavaScript, WebGL-failure, source-failure, and air-gapped behavior.

Leaflet/OpenLayers, deck.gl, WMS/WMTS/WFS, arbitrary projections, drawing, terrain, globe, routing,
geocoding, and offline-region download are not in the Supported inventory.

Authority: [Maps API](../api/MAPS.md) · [RFC-0074](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0074-FIRST-CLASS-MAPS.md).

Try the package-native simulations: [marker filtering](../guides/maps.md#try-markers-and-filtering-simulated)
and [GeoJSON layer accessibility](../guides/maps-accessibility.md#try-the-semantic-alternative-simulated).
Each page includes the complete runnable Hedron app; the docs simulations make no live tile
requests.
