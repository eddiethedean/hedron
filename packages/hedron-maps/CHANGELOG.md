# Changelog

## [1.0.5] — 2026-09-01

- Maintenance release for the coordinated 1.0 train.

## [1.0.4] — 2026-08-31

- Maintenance release for the coordinated 1.0 train.

## [1.0.3] — 2026-08-31

- Maintenance release for the coordinated 1.0 train.

## [1.0.2] — 2026-08-31

### Security

- Reject dot-segment, encoded, and backslash traversal in path-scoped tile allowlists.

## [1.0.1] — 2026-08-30

- Maintenance release for the coordinated 1.0 train.

## [1.0.0] — 2026-08-29

### Changed

- Graduate the bounded MapSpec/MapPlan grammar, first-party component, semantic fallback,
  declared providers, and offline inventory to the Stable 1.0 API.
- Keep unsupported providers, arbitrary projections, and deferred GIS features excluded.

## [0.1.4] — 2026-08-28

### Changed

- Require `hedron-core>=1.0.0,<2.0` for the composable plugin contract.
- Split component, element, MapLibre asset, and catalog registration into focused
  `PluginDefinition` contributions.

## [0.1.3] — 2026-08-27

### Fixed

- Publish the Hedron 1.0-compatible `hedron-core>=0.67.0,<2.0` metadata under a
  new immutable patch version.

## [0.1.2] — 2026-08-26

### Fixed

- Publish a corrected Hedron 0.66-compatible satellite release. The previous
  `0.1.1` PyPI artifact carried a stale `hedron-core<0.62` requirement.

## [0.1.1] — 2026-08-24

### Changed
- Updated the Hedron core compatibility floor for the 0.62 interaction train.

## [0.1.0] — 2026-08-17

### Added

- Independent Beta `hedron-maps` `0.1.0`: typed `MapSpec` / `MapPlan`, `compile_map`,
  `hedron_maps.Map`, OSM preset, custom/offline sources, `hedron-map` host, and
  `MapInteraction` (D-078 / D-082 / RFC-0074).

### Fixed

- ``Map(tiles=)`` preserves existing ``MapPolicy`` fields when appending tile origins
  (no longer resets ``remote_requests_permitted`` / ``allowed_source_kinds`` / ``allow_proxy``).
- Relative ``OpenStreetMap.tile_url`` values no longer forge the public OSM CDN origin.
- Custom ``OpenStreetMap.tile_url`` hosts must pass the same origin allowlist as raster
  tiles (#351).
- ``Map(tiles=)`` uses exact-origin allowlisting instead of empty or host-prefix bypass
  (#352).
- MapStyle source ``data`` / ``urls`` close through origin policy (#353).
- ``MapInteraction`` POSTs typed events to the registered command path with CSRF (#357).
- ``MapPolicy.remote_requests_permitted`` is enforced at compile and proxy time (#363).
- TileJSON / PMTiles / MBTiles emit compiled MapLibre sources; overlay layers fold into the style (#358, #360).
- Zoom ``0`` is preserved; viewport debounce is cleared on dispose; loadScript retries after a failed runtime tag (#359, #361, #362).
- Marker ``href`` is validated at compile; CGNAT and non-global IPs are blocked in map SSRF checks (#364, #365).
