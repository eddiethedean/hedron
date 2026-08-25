# Phase 0.65 upgrade fixtures

Status: **Verified**. These fixtures are covered by the 0.65 regression and evidence checks.

The target package line for every fixture is `v0.65.0`; the baseline remains the published/in-tree
`v0.64.1` compatibility point.

The ejection fixture artifacts are `application-styles.css` and its `source_map.json` sidecar;
the sidecar records source and generated-content digests so edited output is reported as drift.

| Fixture | Baseline | Expected result |
|---|---|---|
| Unused feature | `v0.64.0` / `v0.64.1` app with no registration | byte-compatible styling behavior and no new asset request |
| Registered local CSS | 0.64 app adds one declared stylesheet | one fingerprinted asset, CSP/HTMX-safe head and fragment behavior |
| Layer insertion | existing generated styles plus application stylesheet | deterministic `application` layer between components and utilities |
| Public hook | component gains/uses a manifest-backed part or state | stable hook; private classes remain undocumented and changeable |
| Token collision | app token uses a core token name | deterministic rejection with source and namespace diagnostic |
| Theme change | light/dark/high-contrast/forced-colors selection | app tokens resolve through the existing theme graph with provenance |
| Reduced motion | motion recipe under `prefers-reduced-motion` | animation removed or replaced by a non-motion state-preserving fallback |
| Native control fallback | unsupported control appearance feature | usable native control, focus, invalid and disabled behavior retained |
| Data view state | empty/loading/error/table overflow | semantic state remains available without decorative CSS |
| Ejection | generated surface ejected, then source changed | named generated block diff; update refuses unreviewed drift |
| Removal | registered stylesheet removed | manifest diff identifies removed asset and no stale link is emitted |
| Unsafe source | remote import, unsafe at-rule, private selector, inline CSS | build rejects with redacted actionable diagnostic |
| Explicit global | app opts into global CSS | registration records opt-in, layer, source map, and compatibility impact |
| No JavaScript | full page and fragment with scripts unavailable | styles and semantic fallback remain usable |
