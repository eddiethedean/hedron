# Phase 0.47 upgrade and rollback fixtures

**Status:** Planned<br>
**From:** Verified `v0.46.0`<br>
**To:** `v0.47.0` with optional `hedron-maps` `0.1.0`

Required fixtures:

1. An unchanged `hedron.Map` application with markers, GeoJSON, explicit `tiles`, and
   `tile_allowlist` renders and tests identically without `hedron-maps` installed.
2. The same application migrates explicitly to `RasterTiles` and `MapPolicy`; rendered semantic
   fallback, attribution, origin authorization, and feature actions remain equivalent.
3. An application installs `hedron[maps]`, uses the OSM preset, then replaces it with a custom XYZ
   source without application code outside map configuration changing.
4. A remote map is converted to a closed PMTiles/static-image bundle and passes with external
   network denied.
5. Removing `hedron-maps` and reverting the explicit component import leaves no routes, assets,
   workers, projections, or registry entries.
6. Version skew, missing vendored assets, missing optional archive support, provider outage,
   corrupt archive, CSP denial, and WebGL absence fail with documented diagnostics and useful
   semantic content.
7. Existing `hedron-charts` MapLibre/Folium/PyDeck adapter applications remain explicit and do not
   silently switch to the new package.
