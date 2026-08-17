# Changelog

## [0.1.0] — 2026-08-17

### Added

- Independent Beta `hedron-maps` `0.1.0`: typed `MapSpec` / `MapPlan`, `compile_map`,
  `hedron_maps.Map`, OSM preset, custom/offline sources, `hedron-map` host, and
  `MapInteraction` (D-078 / D-082 / RFC-0074).

### Fixed

- Custom ``OpenStreetMap.tile_url`` hosts must pass the same origin allowlist as raster
  tiles (#351).
- ``Map(tiles=)`` uses exact-origin allowlisting instead of empty or host-prefix bypass
  (#352).
- MapStyle source ``data`` / ``urls`` close through origin policy (#353).
- ``MapInteraction`` POSTs typed events to the registered command path with CSRF (#357).
