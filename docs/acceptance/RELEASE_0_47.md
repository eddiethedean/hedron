# Hedron `v0.47` first-class maps acceptance

**Status:** Planned; Stage 0 contract refined by D-082 against Published in-tree `v0.46.0`<br>
**Planning baseline:** Published in-tree `v0.46.0` (D-082; original Stage 0 baseline was Published in-tree `v0.45.0`)<br>
**Required predecessor/cut baseline:** Verified `v0.46.0`<br>
**Targets:** Hedron `v0.47.0`; `hedron-maps` `0.1.0` Beta<br>
**Decision/RFC:** D-078, refined by D-082 / [RFC-0074](../rfcs/RFC-0074-FIRST-CLASS-MAPS.md)

D-082 rebases planning onto shipped `hedron.Map` / `sanitize_geojson` / `MAP_VIEWPORT_TRIGGER`,
0.43 `ActionHandle`, 0.44 `hedron.type`, 0.45 catalog/projection, and 0.46 `FeatureBundle` /
`ChartInteraction` pattern seams. It does not authorize Stage 1. `MapInteraction` is the maps
event binding. `OpenStreetMap.standard()` is the `hedron_maps.Map` default only.

Implementation requirements:
[HEDRON_MAPS_047](../implementation/HEDRON_MAPS_047.md). Public contract:
[MAPS](../api/MAPS.md). Capability inventory:
[`map-capability-inventory-047.toml`](map-capability-inventory-047.toml).
Spec/plan, provider/policy, offline, and interaction/compat locks:
[`map-spec-plan-047.toml`](map-spec-plan-047.toml),
[`map-provider-policy-047.toml`](map-provider-policy-047.toml),
[`map-offline-047.toml`](map-offline-047.toml),
[`map-interaction-compat-047.toml`](map-interaction-compat-047.toml).
Evidence index: [`release-gate-0.47.toml`](release-gate-0.47.toml). Upgrade fixtures:
[upgrade-fixtures-047](upgrade-fixtures-047.md).

## Release contract

- One-line maps, custom tile infrastructure, and offline/file-backed maps are equal first-class
  paths through one typed grammar.
- Pinned strict-CSP MapLibre is the Supported enhanced renderer but not the public Python API.
- The OSM preset is attributed, policy-aware, replaceable, and not presented as production SLA.
- Plans close over every tile/style/sprite/glyph/image/archive origin and contain no credentials.
- Static images, PMTiles, bounded MBTiles, and blank maps pass network-denied deployment tests.
- Semantic feature/action alternatives survive no JavaScript, WebGL/CSP/source failure, and swaps.
- Existing `hedron.Map` and explicit chart map adapters remain compatible and optional.

## Exact gate matrix

| Gate | Verified means |
|---|---|
| `SPEC-047` | Closed map/basemap/source/layer/style/view/event grammar, deterministic plans/fingerprints, validation, limits, and unknown-field/version failures pass. |
| `PROVIDER-047` | OSM preset, custom XYZ, TileJSON, vector tiles, attribution, exact origins, zoom/bounds/tile metadata, replacement, and provider diagnostics pass. |
| `OFFLINE-047` | Static image, PMTiles raster/vector, bounded MBTiles, blank map, bundle closure, Range/cache/integrity, packaging, and network-denied air-gap paths pass. |
| `RENDER-047` | Pinned strict-CSP MapLibre host, safe style subset, sources/layers/controls/theme/view/failure states, lazy mount, resize, update, and destroy pass. |
| `INTERACT-047` | Stable feature ids, selection/activation/viewport/layer/load/failure payloads, validation, debounce, rate/cardinality, commands/effects, ordinary-action fallback, and races pass. |
| `SECURITY-047` | Origin/template/style closure, credential redaction, popup/GeoJSON safety, CSP, proxy SSRF/redirect/DNS/response bounds, archive path/SQL safety, privacy, and threat review pass. |
| `A11Y-047` | Titles/descriptions, semantic feature/action alternative, keyboard/gesture/focus/popup behavior, non-color state, zoom/reflow/visual modes, and scoped AT honesty pass. |
| `BROWSER-047` | Chromium/Firefox/WebKit enhanced/no-JS/WebGL/CSP/network/worker failures, HTMX swaps, rapid updates, cancellation, reconnect, and cleanup pass. |
| `PERF-047` | Vendored bytes, lazy/interactive timing, layer/feature/plan/style/tile concurrency, long-task, memory, repeated lifecycle, archive, and no-opt-in overhead budgets pass. |
| `ADAPTER-047` | FastAPI/Flask/Django/Posit/Workbench mounts, prefixes, assets, CSP, archives, authz, caching, and limitations pass. |
| `TOOLING-047` | Explorer/CLI/scenario/conformance/sim inspection and offline/provider/style/egress/fallback/event evidence agree without executing untrusted map data. |
| `COMPAT-047` | Existing core Map/chart adapters, direct APIs, install/absence/skew, migrations, rollback, optionality, and previous Supported lines pass unchanged. |
| `DOCS-047` | Quickstart, custom/self-hosted/offline/air-gap/security/a11y/operations/migration/troubleshooting/limitations and provider policy docs are complete. |
| `REGRESS-047` | Full Supported suite passes with zero phase-owned blocker/high regression and no hidden Deferred claim. |
| `PKG-047` | Clean wheel/sdist, assets/licenses/SBOM/provenance, Python/platform matrix, dependency bounds, package data, versioning, changelog, and release rehearsal pass. |

## Stage 0 entry

- [x] D-078 and RFC-0074 define renderer, provider, offline, policy, authority, and compatibility
  boundaries.
- [x] API, package, implementation, inventory, gate, release, upgrade, roadmap, decision, and index
  artifacts exist.
- [x] Stage 0 changes documentation/contracts only; no runtime/package/version availability claim.
- [x] D-082 rebases planning onto Published in-tree `v0.46.0` without runtime/version claim.
- [ ] Verified 0.46 and a tracking issue are bound before Stage 1.
- [ ] Stage 1 measures and locks all default limits and performance budgets.

## Cut rule

Do not cut `v0.47.0` or publish `hedron-maps` `0.1.0` until every row in
[`release-gate-0.47.toml`](release-gate-0.47.toml) is Verified with retained evidence and zero
Deferred rows.
