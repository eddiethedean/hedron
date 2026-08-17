# `hedron-maps` implementation plan (phase 0.47)

**Status:** Published as in-tree `v0.47.0` (tag/PyPI deferred); Stage 0 contract refined by D-082 against Published in-tree `v0.46.0`<br>
**Tracking:** [#350](https://github.com/eddiethedean/hedron/issues/350)
**Decision/RFC:** D-078, refined by D-082 / [RFC-0074](../rfcs/RFC-0074-FIRST-CLASS-MAPS.md)<br>
**Planning baseline:** Published in-tree `v0.46.0`<br>
**Target:** Hedron `v0.47.0`; independent `hedron-maps` `0.1.0` Beta<br>
**Required predecessor:** Verified `v0.46.0`

D-082 does not authorize Stage 1. It names shipped seams `hedron.Map`, `sanitize_geojson`,
`MAP_VIEWPORT_TRIGGER`, `ActionHandle`, `Hedron.include_feature`, and catalog projections.
`MapInteraction` is the ChartInteraction analog. `OpenStreetMap.standard()` is the
`hedron_maps.Map` default only.

## Consume shipped, do not fork

- Core `hedron.Map` / sanitizer `GeoJSONLayer` / `MarkerSpec` / `sanitize_geojson` /
  `tile_allowlist` / `HED-MAP-0001`–`0004`. Core `Map` has no OSM default.
- `MAP_VIEWPORT_TRIGGER = "map.viewport"` — `ViewportChanged` stacks on this dialect.
- 0.43–0.46 handles, `TypeSchema` under `hedron.type`, `InteractionCatalog` /
  `PackageProjection`, `FeatureBundle` (not an executor), `Hedron.include_component` /
  `include_feature` / `interactions`.
- Element ABI / HTMX swap-dispose. Do **not** adopt `[data-hedron-chart="maplibre"]` as the
  Supported maps renderer.

Lock files: [map-spec-plan-047.toml](../acceptance/map-spec-plan-047.toml),
[map-provider-policy-047.toml](../acceptance/map-provider-policy-047.toml),
[map-offline-047.toml](../acceptance/map-offline-047.toml),
[map-interaction-compat-047.toml](../acceptance/map-interaction-compat-047.toml).

## Architecture


The package has five layers with one-way dependencies:

1. **Portable models:** immutable `MapSpec`, basemap/source/layer/style/event/policy values.
2. **Compiler:** validation, normalization, bounds, resource closure, fingerprints, fallback plan,
   renderer and limit decisions.
3. **Hedron component:** SSR configuration and semantic feature navigator/table built on
   `hedron-core` and compatible with the existing `hedron.Map` contract.
4. **Browser host:** ABI-conforming `hedron-map` plus pinned MapLibre strict-CSP assets.
5. **Optional server helpers:** declared MBTiles/archive and credentialed-proxy routes owned by the
   flagship/adapters, never by portable models.

Portable imports must not require FastAPI, MapLibre, Node, sqlite extras, or internet access.
Consumers do not run a Node build. Vendored assets are reproducible, licensed, hashed, and verified
by package-data tests.

## Work packages

### M1 — Package, grammar, and compilation

- Scaffold `packages/hedron-maps` with Python 3.11–3.14 metadata and `hedron-core` dependency.
- Define schema-versioned closed models and canonical JSON/fingerprint rules.
- Implement `compile_map()` with deterministic ordering and no I/O for already materialized specs.
- Bound maps, layers, sources, features, coordinate depth/count, properties, plan/style/GeoJSON
  bytes, zoom, bounds, attribution, controls, and event declarations.
- Produce `MapPlan` sections for renderer, resources, CSP, attribution, fallback, diagnostics,
  interactions, limits, and fingerprints.

### M2 — Basemaps and sources

- Implement OSM standard raster preset and provider metadata/diagnostics.
- Implement exact-origin XYZ raster templates and TileJSON.
- Implement MVT/vector tile sources plus a safe MapLibre-style subset.
- Implement local `StaticImage`, `PMTiles`, `MBTiles`, and `None` basemaps.
- Validate raster/vector MIME, tile size, min/max zoom, bounds, scheme (`xyz`/declared `tms`),
  attribution, and resource consistency.
- Define an extension protocol for third-party provider values without making an open mapping part
  of the Supported parser.

### M3 — Layers, view, theme, and fallback

- Implement marker, bounded GeoJSON, line, polygon, circle, and raster overlay plans.
- Provide explicit `ViewState`, `fit="layers"`, bounds/padding, control placement, light/dark/
  forced-colors tokens, and responsive sizes.
- Reuse or extract current GeoJSON sanitization and feature-table behavior without weakening limits.
- Render titles, descriptions, attribution, feature rows, coordinates, links, and declared ordinary
  actions before enhancement.
- Define empty, loading, unsupported, renderer failure, source failure, and partial-layer states.

### M4 — MapLibre browser host

- Vendor pinned standard and strict-CSP worker builds plus CSS and license inventory.
- Mount only from validated `MapPlan`; do not interpret arbitrary attributes/options as MapLibre
  configuration.
- Implement lazy/eager mount, resize, visibility, color-mode, reduced-motion, controls, layer
  updates, selection, popups, failure reporting, and deterministic destroy.
- Integrate with HTMX before-swap/after-swap, fragment reconnection, rapid updates, aborted fetches,
  worker failures, and duplicate mount prevention.
- Keep MapLibre symbols and event objects behind the host boundary.

### M5 — Typed interactions

- Register closed event payload schemas and map events to ordinary 0.43–0.46 commands/effects.
- Coalesce/debounce viewport completion events; never emit frame-level movement.
- Limit selected ids/properties, payload bytes, frequency, concurrency, and refresh fan-out.
- Use stable ids and server-authoritative revalidation for feature actions.
- Preserve ordinary links/buttons for actions when enhancement is absent.

### M6 — Offline assets and archives

- Define `OfflineMapBundle` manifest, hashes, relative-resource closure, and package-data discovery.
- Serve static images/PMTiles through same-origin asset behavior with Range support where required.
- Add declared MBTiles handles with read-only access, connection lifecycle, XYZ/TMS conversion,
  MIME, cache/ETag/Range behavior, authz hook, integer bounds, cancellation, and concurrent access.
- Test complete network denial, missing resources, corrupt/truncated archives, invalid ranges,
  unsupported compression, oversized files, and package/wheel inclusion.
- Provide a small redistributable test archive generated from synthetic/non-restricted data.

### M7 — Security and provider operations

- Implement parsed URL/origin/template validation and style-resource graph closure.
- Reject credentials/userinfo, dynamic URLs, unsafe schemes, cross-origin redirects, dangerous
  style keys/operators, active popup HTML, and unsafe GeoJSON properties.
- Define optional same-origin proxy integration with SSRF-safe resolution, redirect revalidation,
  network allowlists, response limits, timeouts, cancellation, caching, redaction, and audit.
- Add provider diagnostics for attribution, policy URL, cache behavior, health, range support,
  rate/authorization failures, and public-service production use.
- Generate exact CSP/egress facts for Explorer and deployment policy composition.

### M8 — Accessibility, visual design, and performance

- Specify keyboard behavior, cooperative gestures, focus entry/exit, popup focus, control names,
  target sizes, non-color selection, and map-region labeling.
- Test 200%/400% zoom, reflow, narrow viewports, forced colors, dark mode, reduced motion, RTL,
  localization, long attribution, and missing tiles.
- Attach scoped human keyboard/AT review without claiming spatial canvas equivalence.
- Lock byte, timing, long-task, feature/layer, request-concurrency, memory, swap/leak, and no-opt-in
  overhead budgets from measured baselines before Stage 1 completion.

### M9 — Adapters, tooling, documentation, and release

- Prove FastAPI/Flask/Django and Posit/Workbench mounting, asset prefixes, CSP, archives, and authz.
- Add Explorer inspection for provider, plan, origins, styles, local assets, attribution, limits,
  fallback, failures, and event schemas.
- Add scenario/conformance fixtures and an offline `hedron-sim` subset.
- Publish quickstart, custom XYZ, self-hosted Martin, static image, PMTiles, MBTiles, air-gapped,
  policy, accessibility, operations, migration, troubleshooting, and rollback guides.
- Run clean wheel/sdist/install/absence/skew/license/SBOM/provenance/rehearsal gates.

## Default limits (Stage 1 measured)

| Dimension | Locked default |
|---|---|
| maps/page (`maps_per_page`) | 8 |
| layers/map | 32 |
| sources/map | 16 |
| GeoJSON features | 500 (`DEFAULT_MAX_FEATURES`) |
| coordinate depth | 8 |
| coordinate count | 50_000 |
| property bytes / feature envelope | 4_096 |
| plan bytes | 1_000_000 |
| style bytes | 250_000 |
| TileJSON bytes | 64_000 |
| zoom | 0–24 |
| tile concurrency | 8 |
| event rate / payload / cardinality | 4 Hz / 8_192 / 100 |
| workers | 1 |
| cache memory | 32 MiB |
| proxy response / timeout / redirects | 4 MiB / 5 s / 3 |
| mount/destroy cycles | 100 |

## Default limits to resolve during Stage 1

Stage 0 names the dimensions but does not invent unmeasured numbers. Stage 1 must lock evidence-
backed defaults for: maps/page, layers/map, sources/map, GeoJSON features and coordinates, property
depth/bytes, plan/style/TileJSON bytes, static image/archive bytes, zoom, simultaneous tile
requests, event rate/payload/cardinality, worker count, cache memory, proxy response/time/redirects,
and repeated mount/destroy cycles. Defaults become public compatibility facts once cut.

## Failure and diagnostic families

Reserve documentation namespaces `HED-MAP-SPEC-*`, `HED-MAP-SOURCE-*`, `HED-MAP-STYLE-*`,
`HED-MAP-POLICY-*`, `HED-MAP-OFFLINE-*`, `HED-MAP-RUNTIME-*`, and `HED-MAP-EVENT-*`. Existing
`HED-MAP-0001`–`0004` behavior remains compatible. Exact new code numbers are assigned only with
implementation and error-code documentation.

## Stage ordering

- **Stage 0:** accepted contracts, complete planning packet, D-082 consume-shipped locks,
  no runtime/version claim.
- **Stage 1:** after Verified 0.46 and a tracking issue; measure baselines and implement M1–M3.
  Do not start Stage 1 during the D-082 contract refine.
- **Stage 2:** M4–M7 browser/offline/security vertical slices.
- **Stage 3:** M8–M9 whole-matrix evidence, docs, package/release rehearsal.
- **Cut:** every 0.47 gate Verified with zero Deferred. In-tree Published `v0.47.0`;
  Git tag / PyPI remain deferred. Do not tag `v0.47.0` or publish `hedron-maps` until
  a later registry cut.
