# Upgrade fixtures — phase 0.38 high-fidelity charts

Stage 0 contract refine baseline: living Published `v0.38.0`. Runtime implementation begins at
Stage 1. Cut targets: Hedron `v0.38.0`, independent `hedron-charts` `0.2.0`. Tracking
[#251](https://github.com/eddiethedean/hedron/issues/251).

## Required upgrade corpus

- Beginner components (`LineChart`, `AreaChart`, `BarChart`, `ScatterChart`) retain source call
  shapes and compile to stable `ChartSpec` fixtures.
- Matplotlib SVG/PNG retains Supported accessibility, security, export, payload, and fallback
  behavior.
- 0.1 Plotly/Altair explicit components continue as Experimental opt-ins; no import or Auto path
  silently changes them into the first-party renderer.
- Common Plotly/Altair examples produce a migration report with converted fields and explicit
  unsupported features; conversion never drops traces/transforms/interactions silently.
- Current chart event fixtures map to versioned 0.38 kinds in [CHART_SPEC.md](../implementation/CHART_SPEC.md)
  or emit a named remediation diagnostic.
- Current CSS overrides map to public chart tokens or are identified as private/unsupported.
- JavaScript-off/static-only deployments retain semantic figure/summary/table/export fallbacks.
- HTMX inner/outer/OOB lifecycle fixtures from `hedron-charts` 0.1.11 remain green under 0.2.

## Pin migration at cut

| Surface | Before | At phase 0.38 cut |
|---|---|---|
| Hedron train | `hedron>=0.38.0,<0.39` | `hedron>=0.38.0,<0.39` |
| Charts Supported 0.1 line | `hedron-charts>=0.2.0,<0.3` | `hedron-charts>=0.2.0,<0.3` |
| Matplotlib static | Supported | Supported |
| First-party interactive | Not available | Supported declared 0.38 inventory |
| Plotly/Altair/vendor adapters | Experimental | Experimental explicit opt-in |

## Rollback

Rollback removes `ChartSpec`/`Chart` usage or replaces it with beginner/Matplotlib components,
pins `hedron-charts>=0.2.0,<0.3`, removes 0.2-only assets, and verifies no stale custom-element
definition or cached asset remains. Exported canonical data remains portable; browser-local
selection/zoom state is disposable and is not migrated as server authority.

## Required artifacts

- before/after markup, normalized plan, screenshot, accessibility tree, and export goldens;
- schema upgrade and unknown-version negative fixtures;
- three-browser persisted-cache/version-skew and rollback tests;
- clean wheelhouse install for 0.1 → 0.2 and 0.2 → 0.1 rollback documentation;
- migration report fixtures that prove unsupported vendor features are never silently discarded.
