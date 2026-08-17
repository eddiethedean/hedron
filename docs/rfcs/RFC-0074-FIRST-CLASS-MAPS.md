# RFC-0074: First-class maps and offline geospatial presentation

**Status:** Accepted<br>
**Target phase:** 0.47 (`v0.47.0`)<br>
**Decision:** D-078<br>
**Planning baseline:** Published in-tree `v0.45.0`<br>
**Required predecessor/cut baseline:** Verified `v0.46.0`<br>
**Package target:** `hedron-maps` `0.1.0` (Beta for its declared Supported inventory)<br>
**Extends:** RFC-0011, RFC-0012, RFC-0014, RFC-0018, RFC-0019, RFC-0020,
RFC-0021, RFC-0023, RFC-0024, RFC-0025, RFC-0028, RFC-0033, RFC-0040,
RFC-0051, RFC-0053, RFC-0056, RFC-0060, RFC-0070, RFC-0072, and RFC-0073

**Revision:** 2026-08-16 — D-079 rebases 0.46 planning onto Published in-tree `v0.45.0`
without changing this RFC's maps authority, planning baseline, Stage 0/1 gates, or
`hedron-maps` `0.1.0` target.

## Summary

Phase 0.47 makes geographic presentation a first-class Hedron experience through a new optional
`hedron-maps` distribution. A one-line `Map()` produces a useful, attributed OpenStreetMap-backed
development experience; typed basemaps, sources, layers, styles, policies, and plans make custom
tile infrastructure equally natural. Static images, blank canvases, PMTiles, and bounded MBTiles
serving provide deliberate no-internet and air-gapped paths.

The Supported enhanced renderer is a pinned, locally shipped, strict-CSP MapLibre GL JS host behind
the existing Web Component lifecycle. MapLibre is an implementation detail: applications author a
closed Python map grammar and `compile_map()` emits an immutable `MapPlan`. The existing
`hedron.Map` / `GeoJSONLayer` presentation remains available and supplies the compatibility and
semantic fallback boundary.

## Goals

- Make `Map()` useful with no provider configuration while keeping provider terms and operational
  limitations visible.
- Treat custom XYZ raster, TileJSON, MVT/vector tile, local style, static image, PMTiles, and
  bounded MBTiles sources as typed first-class inputs.
- Separate `Basemap`, `Source`, `Layer`, `MapStyle`, `MapPolicy`, `MapSpec`, and `MapPlan` so simple
  usage does not constrain advanced deployments.
- Support internet-free and air-gapped applications without silently reaching remote origins.
- Compile every style/source/resource reference into an inspectable egress, CSP, attribution, and
  asset manifest.
- Provide typed feature and viewport interactions through ordinary Hedron commands and effects.
- Preserve semantic feature navigation, tabular alternatives, and useful failed/no-JavaScript
  output.
- Ship an optional package with no consumer Node build and no MapLibre or provider API leakage in
  the public Python contract.

## Non-goals

- A general GIS desktop, tile-authoring pipeline, spatial database, geocoder, router, or tile CDN.
- Automatic discovery of credentials, provider accounts, licensing rights, or acceptable traffic.
- Arbitrary MapLibre JavaScript, callbacks, expressions, plugins, remote styles, or executable
  popup HTML.
- WMS/WMTS/WFS, arbitrary coordinate reference systems, terrain, globe, 3D Tiles, drawing/editing,
  offline-region download, or deck.gl in the initial Supported inventory.
- Treating browser map state, feature properties, geolocation, or tile possession as authorization.
- Promising availability for community OpenStreetMap infrastructure.
- Replacing `hedron.Map`, making WebGL mandatory for content access, or scheduling Hedron `1.0`.

## Public conceptual model

`MapSpec` is an immutable, versioned declaration containing:

- one optional `Basemap`;
- a bounded ordered sequence of typed layers;
- initial `ViewState` or an explicit fit policy;
- controls, interaction declarations, theme, accessibility description, and failure behavior; and
- an optional application `MapPolicy` reference resolved before compilation.

`compile_map(spec, policy=...)` validates and normalizes the declaration into a deterministic
`MapPlan`. The plan contains only JSON-compatible inert data: normalized view and layer data,
renderer choice, local asset references, exact remote origins, CSP requirements, attribution,
fallback content, bounds, limits, warnings, and stable fingerprints. It contains no secrets,
callables, open file handles, ambient environment reads, or executable source strings.

The initial public families are:

- basemaps: `OpenStreetMap`, `RasterTiles`, `TileJSON`, `VectorTiles`, `StaticImage`, `PMTiles`,
  `MBTiles`, and `NoBasemap` / `None`;
- layers: `MarkerLayer`, `GeoJSONLayer`, `LineLayer`, `PolygonLayer`, `CircleLayer`, and
  `RasterLayer`;
- presentation: `Map`, `MapTheme`, `MapStyle`, `ViewState`, `Bounds`, and controls;
- policy/compilation: `MapPolicy`, `MapSpec`, `MapPlan`, `compile_map`; and
- events: `FeatureSelected`, `FeatureActivated`, `ViewportChanged`, `LayerVisibilityChanged`,
  `MapLoaded`, and `MapFailed`.

## Provider and OpenStreetMap contract

`Map()` selects a versioned `OpenStreetMap.standard()` preset with the exact HTTPS raster endpoint,
visible `© OpenStreetMap contributors` attribution, zoom limits, no bulk prefetch, and ordinary
browser caching. The preset is a replaceable default, not an SLA or production-capacity claim.
Explorer and production diagnostics identify use of the community service and link operators to
its current usage policy.

Provider presets contain declarative source metadata, required attribution, zoom/bounds, tile size,
terms/operations links, and a stable id. A preset may authorize only its declared exact origins.
The first-party catalog stays deliberately small; commercial providers and credentials are not
silently bundled. Third-party packages may publish provider values through ordinary plugin and
projection contracts.

Custom URLs are parsed structurally. Supported templates use a closed placeholder inventory
(`{z}`, `{x}`, `{y}`, and explicitly enabled scale/subdomain placeholders), HTTPS for remote
production sources, exact origin and optional path constraints, bounded zoom, and mandatory
attribution declarations. User- or request-supplied provider URLs are rejected.

## Offline and file-backed contract

Offline is a tested deployment mode with four distinct paths:

1. `StaticImage` serves a packaged PNG/JPEG/WebP/AVIF with declared geographic bounds and optional
   SVG/DOM overlays. Without bounds it is a non-georeferenced accessible image.
2. `PMTiles` reads raster or vector tiles from a same-origin HTTP Range-capable packaged asset.
   Vector use requires all styles, sprites, glyphs, and other resources to resolve locally unless
   policy explicitly permits remote origins.
3. `MBTiles` exposes a declared server-local archive through a bounded, same-origin, cache-aware
   application route. The route is not a general tile server and never accepts a filesystem path
   from a request.
4. `basemap=None` renders overlays on a blank canvas and is valid for floor plans, site maps,
   fictional geography, and privacy-sensitive applications.

`OfflineMapBundle` validates a directory manifest containing an archive or image, style, sprites,
glyphs, attribution, hashes, bounds, and packaging metadata. Air-gapped acceptance runs with
network denied and fails on any undeclared external reference. Browser applications access
packaged files through same-origin asset routes; arbitrary `file://` browser access is excluded.

## MapLibre host and progressive enhancement

The Supported enhanced path vendors pinned MapLibre GL JS assets, including its strict-CSP worker
bundle. No CDN script is loaded. The `hedron-map` element consumes a bounded `MapPlan`, mounts only
when visible or explicitly eager, observes resize, reports typed load/failure state, and disposes
maps, workers, observers, listeners, object URLs, pending requests, and optional adapters on HTMX
swap or disconnect.

MapLibre style documents are data but cross a security boundary because they reference tiles,
sprites, glyphs, images, and expressions. Hedron accepts a locked safe style subset for Supported
authoring, validates every resource URL and expression/operator, rejects prototype-pollution keys
and executable values, and records a canonical fingerprint. An explicit Experimental escape hatch
may accept reviewed vendor styles but cannot inherit Supported claims.

Enhancement failure never removes the server-rendered title, description, attribution, feature
list/table, links, or actions. WebGL absence, worker failure, CSP denial, malformed tiles, network
loss, and reduced-capability browsers produce an owned failure state.

## Interactions and application authority

Feature and viewport events use closed, versioned payload models. Feature events carry stable
application-declared ids and bounded public properties, never authoritative hidden properties.
Viewport events carry center, zoom, and bounded coordinates only after coalescing/debounce; they do
not stream every frame. Events invoke existing commands and effects and repeat normal validation,
CSRF, authentication, authorization, rate, and target checks.

Popups contain Hedron-rendered safe nodes or plain text. Arbitrary HTML and browser callbacks are
not accepted. Geolocation is explicit, permission-gated, spoofable, and never an authorization
factor. Server commands remain authoritative for selection consequences and protected data.

## Security and privacy requirements

- `MapPolicy` declares exact origins, HTTPS rules, local asset roots/ids, allowed source kinds,
  maximum zoom/features/layers/coordinates/payload/archive sizes, interaction rates, and whether
  remote requests are permitted.
- Compilation recursively inventories style, TileJSON, sprite, glyph, image, archive, and tile
  origins and fails closed on unknown or policy-disallowed resources.
- URL userinfo, embedded bearer/API secrets, protocol-relative URLs, unsafe schemes, redirects to
  unapproved origins, DNS/private-network proxy targets, and request-derived URLs fail closed.
- Browser-visible plans, HTML, logs, errors, manifests, fingerprints, snapshots, and Explorer
  views contain no credentials.
- Credentialed upstreams use an application-defined same-origin endpoint or explicit bounded proxy
  policy with live authorization, SSRF defenses, redirect limits, timeouts, response/type/size
  bounds, cache rules, audit, and secret redaction.
- Remote maps disclose third-party requests and privacy consequences; no location or feature data
  is sent to a tile provider beyond normal tile coordinates.
- Archive routes validate declared handles and integer z/x/y ranges; they never concatenate request
  values into paths or SQL.

## Accessibility requirements

- Every map has an author-facing title and useful description or an explicit reviewed decorative
  disposition.
- Every meaningful feature and action is reachable through a semantic list/table or equivalent
  ordinary links/buttons independent of canvas hit testing.
- Enhanced controls have accessible names, visible focus, documented keyboard behavior, minimum
  target sizes, high-contrast/forced-colors treatment, and reduced-motion behavior.
- Cooperative gestures prevent accidental page-scroll capture; Escape or moving focus leaves the
  map, and zoom/pan never creates a keyboard trap.
- Selection, hover, and layers do not rely on color alone. Popups have managed focus and a usable
  close path.
- Automated checks and scoped keyboard/AT evaluation are required; no blanket claim that a canvas
  representation itself exposes all spatial relationships to assistive technology is permitted.

## Performance and operational requirements

The release records budgets for initial vendored JS/CSS/worker bytes, lazy-load cost, time to
fallback, time to interactive map, tile concurrency, layer/feature/coordinate counts, GeoJSON and
plan bytes, worker/main-thread long tasks, memory after repeated swaps, and cleanup. Applications
without `hedron-maps` load no map assets or request-path work.

Tile failures are observable without logging secrets. Provider health distinguishes configuration,
DNS/TLS, authorization, rate limiting, invalid content, range support, archive integrity, and
renderer failure. Cache behavior honors upstream headers and provider terms; the package does not
implement offline-region prefetch against public services.

## Compatibility, migration, and rollback

Existing `hedron.Map(center=..., tiles=..., tile_allowlist=..., markers=..., geojson=...)` remains
unchanged. `hedron-maps.Map` may accept a compatibility constructor and compile to the same semantic
fallback. Migration documentation maps `tiles` plus `tile_allowlist` to `RasterTiles` plus
`MapPolicy`; no existing call silently gains remote access or MapLibre assets.

The package is optional via `hedron[maps]` or direct `hedron-maps`. Removing it returns applications
to `hedron.Map` or static content without changing core routing. `hedron-charts` MapLibre/Folium/
PyDeck adapters remain explicit visualization adapters until separately migrated; phase 0.47 does
not silently promote them.

## Alternatives considered

1. **Leaflet as the sole renderer.** Excellent for raster/marker maps and retained as a possible
   lightweight adapter, but not selected as the platform because first-class vector styles and
   scalable future layers would depend on plugins or a later renderer change.
2. **OpenLayers as the sole renderer.** Broad GIS and projection support, but too low-level and
   expansive for the initial beginner contract; appropriate for a later advanced GIS adapter.
3. **deck.gl as the root.** Strong dense visualization, but it is not the desired default basemap
   and adds substantial runtime. It remains an optional future overlay.
4. **Remote-provider iframe.** Avoids a runtime but weakens policy, composition, offline behavior,
   interactions, and accessibility.
5. **Only static images.** Valuable and Supported, but insufficient as the complete first-class
   interactive experience.

## Resolved questions (D-078)

1. **Renderer?** Pinned local strict-CSP MapLibre for the Supported enhanced path.
2. **Default provider?** Replaceable OSM standard raster preset with attribution and operational
   diagnostics; no SLA claim.
3. **Is MapLibre the public API?** No. Closed Hedron models compile to `MapPlan`.
4. **Are offline files first-class?** Yes: static images, PMTiles, bounded MBTiles, and blank maps.
5. **Can styles load arbitrary resources?** No. Complete resource closure is validated against
   `MapPolicy`; remote reviewed styles remain Experimental.
6. **Do credentials go in tile URLs?** No Supported path exposes credentials to HTML/plans.
7. **Is MBTiles a general tile server?** No. It is a declared archive route with fixed policy.
8. **Are map events authoritative?** No. They are untrusted command inputs.
9. **Does the map replace accessible content?** No. Semantic alternatives are required.
10. **What is the release baseline?** Verified 0.46 is required before Stage 1 or the 0.47 cut.

## Acceptance criteria

- Zero-config, custom raster, TileJSON/vector, static image, PMTiles, MBTiles, and blank-map vertical
  slices pass their declared Supported matrices.
- An air-gapped example passes with network denied and no missing style/sprite/glyph/archive asset.
- OSM attribution and usage-policy behavior are correct and provider replacement is documented.
- Exact-origin, style-resource closure, credential redaction, proxy SSRF, archive traversal, hostile
  GeoJSON/style, and payload/resource bounds pass adversarial tests.
- Native/fallback, enhanced, failed-upgrade, no-JavaScript, WebGL failure, HTMX swap, and three-engine
  lifecycle paths pass with no content/action loss.
- Keyboard, responsive zoom, forced colors, reduced motion, feature alternatives, and scoped AT
  evidence pass without overstated canvas accessibility.
- Existing `hedron.Map` and chart map adapters pass unchanged; install/absence/skew/rollback and
  clean wheel/source package tests pass.
- Every `release-gate-0.47.toml` row is Verified with zero Deferred before `v0.47.0` is cut.
