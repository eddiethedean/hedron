# RFC-0033: Map and GeoJSON presentation

**Status:** Implemented
**Phase:** 0.15 (`v0.15.0`)
**Related:** [NiceGUI feature cross-check](../NICEGUI_FEATURE_CROSSCHECK.md) (`ui.leaflet`);

## Summary

Add a first-party, policy-bounded `Map` / GeoJSON presentation adapter so data apps can show
geographic context without adopting Leaflet/Vue as a general client runtime. Marker/popup and
viewport interactions become declared HTMX actions or fragment updates; static and keyboard
alternatives remain Required.

## Motivation and background

The 0.15 exit gate already requires diagrams/maps in the reference app, and NiceGUI’s `ui.leaflet`
validates demand. Hedron must not ship an unbounded map runtime that loads arbitrary remote
scripts, tiles, or JavaScript by default (non-goals: SPA/Vue client; D-013 trust boundaries).

## Proposed design

- Public components (names TBD at acceptance): `Map` and/or `GeoJSONLayer` over pinned local assets.
- Props cover center/bounds/zoom, CRS assumptions, GeoJSON FeatureCollection input bounds, marker
  collections with stable identities, attribution, tile/source allowlists, and height/sizing.
- Marker click, selection, and bounded viewport changes submit typed action/query payloads — not
  opaque client callbacks.
- Default tile/script sources are local or explicitly allowlisted; CSP and SRI follow RFC-0021.
- No-JavaScript / reduced-capability path: table or list of features with coordinates and links;
  map chrome must not be the only way to reach content.
- Explorer/CLI explain inference for assets, CSP capabilities, and action targets.

## Alternatives considered

1. **Recipe-only Leaflet embed via `IFrame`/`TrustedHtml`.** Rejected as sole answer — no shared
   policy, a11y, or action contracts; still allowed as an escape hatch.
2. **Full NiceGUI/Leaflet parity (draw tools, plugins, JS APIs).** Rejected — expands browser
   runtime without request/action boundaries.
3. **Server-rendered static map images only.** Insufficient for interactive selection; may remain a
   fallback adapter.

## Security implications

Tile/CDN allowlists, CSP, referrer policy, GeoJSON size/feature budgets, URL safety (`SafeUrl`),
and no execution of properties from untrusted GeoJSON. Map interactions must not bypass
`FragmentRegion` authorization.

## Accessibility implications

Keyboard-operable feature list alternative; visible focus for selectable markers when enhanced;
color-not-sole cue; zoom/pan must not trap focus; reduced-motion for non-essential transitions;
screen-reader name/description for the map region.

## Performance implications

Asset weight budgets, feature-count limits, debounce for viewport events, lazy mount optional.
Observability: asset load failures and oversized GeoJSON diagnostics (`HED-*`).

## Testing strategy

Unit (GeoJSON bounds/validation), integration (action payloads, CSP headers), browser (keyboard
alternative, marker select, zoom), adversarial (malicious GeoJSON, disallowed tiles), a11y suite.

## Compatibility and migration

New opt-in components/extra; no break to existing chart adapters. NiceGUI migration glossary maps
`ui.leaflet` → this RFC.

## Accepted decisions (0.15)

1. **Package ownership:** first-party `Map` / `GeoJSONLayer` live in `hedron-core` (presentation).
   `hedron-charts` MapLibre/Folium/PyDeck remain optional visualization adapters, not this contract.
2. **Basemap day one:** allowlisted tile/script sources plus mandatory static/table fallback; OSM or
   other CDNs are Supported only when explicitly allowlisted by the app policy.
3. **Viewport events:** continuous pan/zoom streaming is Deferred to 0.17; 0.15 ships marker/selection
   as declared actions plus bounds props for initial view.

## Acceptance criteria

- Reference app shows a map with GeoJSON and an ordinary HTTP/table alternative.
- Disallowed tile/script sources fail closed with diagnostics.
- Exit evidence included in the 0.15 release gate for map/CSP/a11y/adversarial rows.
