# RFC-0069: High-fidelity declarative charts

**Status:** Accepted  
**Target phase:** 0.38 (`v0.38.0`)  
**Package cut:** `hedron-charts` `0.2.0`  
**Decision:** D-066  
**Extends:** RFC-0011, RFC-0020, RFC-0021, RFC-0022, RFC-0023, RFC-0025,
RFC-0059, and RFC-0060

**Revision:** 2026-08-14 — D-066 contract refine against Published `v0.37.0`:
resolved questions locked, catalogs in
[CHART_SPEC.md](../implementation/CHART_SPEC.md), tracking
[#251](https://github.com/eddiethedean/hedron/issues/251), medium remediations
#71/#72/#75/#81/#82/#83/#201/#239 bound to 0.38 gates. Prior: Stage 0 packet
inserted the phase after 0.37 and re-homed former 0.38–0.41 Web Component
capabilities to 0.39–0.42.

**Tracking:** [#251](https://github.com/eddiethedean/hedron/issues/251)

> **Implementation note:** This Accepted RFC records the target contract and quality bar. It is not
> an exhaustive statement of `hedron-charts 0.2.0` runtime coverage. See the public
> [Chart API coverage matrix](../api/CHART.md#compiler-contract-versus-current-host-coverage) for
> the current specialized painters, emitted interactions, transforms, exports, and enforced
> bounds. Where the implementation is narrower, the public API page and source are authoritative.

## Summary

Phase 0.38 turns `hedron-charts` from a production-grade static-chart package with Experimental
interactive adapters into Hedron's first-party, high-fidelity visualization platform. The quality
bar is D3-class precision and interaction: excellent scales, axes, marks, labels, responsive
layout, animation, direct manipulation, accessibility, theming, and export. D3 is an implementation
foundation, not the public API and not a claim that every D3 example becomes a Supported chart.

The phase introduces a versioned, typed `ChartSpec` and normalized `ChartPlan`; a local,
fingerprinted, modular D3 renderer; an ABI-conforming `hedron-chart` element; and one semantic model
shared by static fallback, interactive rendering, events, Explorer, tests, and export. Raw JavaScript
callbacks, remote runtime/data loading, and backend-specific JSON are not part of the Supported
contract.

This phase is inserted after 0.37. The previously planned Web Component phases move without scope
loss: rich-surface convergence to 0.39, authoring/interoperability to 0.40, composition/navigation
to 0.41, and production-grade Web Component graduation to 0.42.

## Problem

The current package has strong security and packaging foundations, but its first-party beginner
charts are intentionally small and static. Interactive quality comes from Experimental Plotly,
Altair/Vega-Lite, ECharts, Chart.js, and other adapters whose specifications, behavior, styling,
events, lifecycle, and accessibility differ. That creates five product problems:

1. Hedron cannot offer a coherent, excellent default interactive chart experience.
2. Authors must learn backend-specific dictionaries to get beyond the beginner components.
3. Cross-filtering, selection, annotation, export, and responsive behavior vary by backend.
4. Accessibility and visual quality are mostly adapter obligations rather than grammar invariants.
5. Large third-party runtimes can become an attractive shortcut even when a smaller first-party
   renderer would be safer, faster, and more consistent.

## Goals

- Make a first-party Hedron chart the recommended interactive default.
- Reach publication-quality visual output across common analytical chart families.
- Make sophisticated charts declarative and typed without exposing JavaScript execution.
- Preserve useful SSR/JavaScript-off output and ordinary HTTP/HTMX behavior.
- Give keyboard and assistive-technology users equivalent access to data and operations.
- Make rendering, interaction, export, and performance deterministic enough to gate in CI.
- Retain Matplotlib as a Supported static/export path and vendor adapters as conspicuous,
  separately versioned Experimental integrations.

## Non-goals

- Reimplementing every D3 gallery example, Vega-Lite transform, Plotly trace, GIS renderer, graph
  layout, or 3D/WebGL engine.
- A notebook-style arbitrary Python/JavaScript callback surface.
- Remote scripts, fonts, data, maps, images, or module loading by default.
- Client-side authorization, business validation, durable state, or live-transport correctness.
- Pixel identity between the browser renderer and Matplotlib fallback.
- Requiring Node.js or a bundler in consuming Python applications.
- Graduating every existing optional adapter or making `hedron-elements` production-grade early.

## Public model

### `ChartSpec`

`ChartSpec` is immutable, JSON-serializable, schema-versioned, and validated before rendering. Its
Supported surface contains:

- data references or bounded inline rows with explicit field types and stable row/series keys;
- mark definitions for line, area, bar, point/bubble, rect/heatmap, rule, box, arc, and financial
  OHLC/candlestick compositions;
- positional, color, size, opacity, shape, stroke, detail, grouping, ordering, and tooltip encodings;
- linear, log, symlog, power, time, UTC, ordinal, point, band, and quantized scale definitions;
- axes, legends, titles, captions, annotations, reference lines/bands, and faceting/small multiples;
- explicit transforms for filter, calculate-from-safe-operators, aggregate, bin, stack, window,
  sort, fold, and bounded sampling;
- responsive layout, aspect/min/max size, theme, locale/timezone, renderer preference, motion, and
  export policy;
- declared selection, hover/focus, tooltip, brush, zoom/pan, legend-filter, and drill intent.

There are no executable expressions. Calculations use a closed typed operator catalog. Unknown
schema versions, fields, operators, mark properties, prototype-pollution keys, or event payload
shapes fail with `HED-CHART-*` diagnostics.

### `ChartPlan`

Compilation normalizes a spec into a deterministic `ChartPlan` with inferred domains, resolved
scale/guide definitions, transformed data, mark counts, renderer choice, accessibility model,
asset manifest, export capabilities, warnings, and stable fingerprints. Inference is inspectable;
authors can lock any inferred value. The plan is the unit consumed by the browser host, static
fallback, Explorer, conformance fixtures, caching, and diagnostics.

### Beginner API compatibility

`LineChart`, `AreaChart`, `BarChart`, and `ScatterChart` keep their current call shapes. They compile
to `ChartSpec` and receive the new quality by default. A new `Chart(spec=...)` is the advanced
entry point. `MatplotlibChart` remains Supported. `PlotlyChart` and `AltairChart` remain explicit
Experimental adapters; backend dictionaries never become `ChartSpec` by implication.

## Supported chart catalog

The 0.38 Supported catalog prioritizes depth over novelty:

- line and multi-series line, area and stacked area;
- vertical/horizontal bar, grouped/stacked/diverging bar, waterfall, and bullet;
- scatter and bubble, histogram, density, box plot, and strip/dot distributions;
- heatmap and matrix;
- OHLC/candlestick with volume composition;
- pie/donut only with bounded category and labeling rules;
- layered charts, faceted/small-multiple charts, annotations, reference lines/bands, and shared
  crosshair/tooltip/selection behavior.

Sankey, chord, hierarchy, network, geographic, 3D, and WebGL renderers remain Experimental unless
they independently satisfy every 0.38 gate. Maps stay under the existing map/GeoJSON contract.

## Rendering architecture

The browser renderer is a standards-native `hedron-chart` custom element conforming to the
published element ABI. The shipped runtime is built from pinned D3 modules selected by capability,
tree-shaken into reproducible local assets, and fingerprinted in the wheel. It uses:

- SVG for semantic, inspectable charts up to a measured mark threshold;
- Canvas for dense marks after an explicit, inspectable renderer decision;
- an HTML accessibility and interaction layer independent of the paint surface;
- optional worker preprocessing only when bounded, cancellable, and cleanly disposable.

Renderer selection must not silently change scales, aggregation, selection identity, accessible
content, or export meaning. WebGL is not required and remains Experimental. Routes without charts
load no chart runtime. Python consumers install prebuilt assets and never require Node.js.

## Visual-quality contract

High fidelity is a tested contract, not a stylesheet adjective:

- scales use stable nice-domain/tick algorithms and explicit zero/log/symlog rules;
- bar charts default to a zero baseline; non-zero truncation requires an explicit override and
  visible disclosure;
- missing, invalid, infinite, duplicate, timezone-ambiguous, and out-of-domain data have locked
  diagnostics/dispositions;
- labels, axes, legends, annotations, and tooltips use collision/overflow strategies rather than
  clipping or accidental overlap;
- responsive modes deliberately reduce ticks, labels, legend placement, and facets at named
  breakpoints without changing data meaning;
- palettes are perceptually ordered where appropriate, color-vision-deficiency aware, themeable,
  and never the only carrier of essential meaning;
- typography, grid lines, focus rings, hover targets, density, and whitespace follow public chart
  tokens and work in light, dark, high-contrast, forced-color, print, and reduced-motion modes;
- number/date/time formatting is locale-aware and timezone-explicit; bidirectional labels are
  isolated correctly.

A reviewed visual corpus covers every Supported family at compact, ordinary, and wide viewports,
light/dark/forced-color themes, representative locales, empty/one/many/invalid values, long labels,
and dense data. Structural assertions detect clipping and overlap; screenshots catch aesthetic
regressions. Golden changes require an attached before/after review, not blind snapshot updates.

## Interaction contract

Pointer, keyboard, and touch operate on stable datum/series identities, not incidental DOM nodes.
Supported interactions include focus navigation, inspect/tooltip, series visibility, point/range
selection, crosshair, brush, zoom/pan/reset, and declared drill intent. Every interaction has:

- a typed versioned event and bounded payload;
- an accessible non-pointer path and visible focus;
- reduced-motion and coarse-pointer behavior;
- an explicit local-versus-server authority classification;
- HTMX inner/outer/OOB swap, history, disconnect, and late-response behavior;
- deterministic cleanup of listeners, observers, timers, workers, Canvas state, and object URLs.

Hover alone never exposes unique information. Tooltips are plain structured content, not raw HTML.
Selection never authorizes a server mutation; registered actions still apply ordinary authz/CSRF.

## Accessibility contract

Every chart requires a useful title and purpose/description. The compiler produces an accessible
model containing a concise summary, encoding explanation, key extrema/trends where deterministic,
annotations, interaction help, and a bounded table/download path. Authors review generated prose;
Hedron does not claim automated insight correctness.

SVG charts expose meaningful groups and focus targets without flooding the accessibility tree.
Canvas charts retain an equivalent HTML interaction model. Large tables are bounded and may use a
summary plus authorized CSV export. Keyboard and screen-reader workflows cover data inspection,
series navigation, selection, zoom reset, legend filtering, annotations, and fallback recovery.

## Performance budgets

The cut records exact browser/hardware runners and raw artifacts. At minimum:

- core renderer asset: at most 90 KiB gzip; all first-party 0.38 chart chunks used by the reference
  gallery: at most 160 KiB gzip; no-chart route delta: 0 bytes;
- 1,000-mark initial interactive render p95 at most 150 ms and update p95 at most 75 ms on the
  recorded Chromium CI runner;
- 10,000-mark dense scenario p95 at most 400 ms with no task over 150 ms; larger accepted inputs
  require an explicit bounded aggregate/sample/Canvas plan;
- pointer/keyboard inspect response p95 at most 50 ms and resize p95 at most 100 ms;
- 100 mount/update/disconnect cycles leave no live chart instances and no material retained-heap
  growth beyond the recorded noise allowance;
- layout-shift, label-overlap, payload, transformed-row, facet, mark, and event-rate budgets are
  machine enforced.

Thresholds may be tightened after Stage 1 baselining. Loosening any locked threshold requires a
decision amendment with evidence; the cut cannot replace a failed budget with prose.

## Export and reproducibility

Supported export includes deterministic SVG, scale-aware PNG, canonical CSV/JSON for authorized
data, and print output. Export uses the normalized plan, records schema/theme/locale/timezone and
data fingerprint metadata, excludes secrets, and never fetches remote assets. Browser and server
exports must agree semantically even when paint details differ. Fonts and licenses are explicit.

## Security and supply chain

- Reject JavaScript callbacks, expressions outside the safe operator catalog, event-handler keys,
  raw HTML, unsafe URLs, remote schemas/data/assets, active SVG, and dangerous object keys.
- Bound rows, fields, transforms, facets, marks, labels, string lengths, payload bytes, recursion,
  worker memory, event rate, and export dimensions before allocation or DOM creation.
- Enforce CSP and Trusted Types with no `unsafe-eval` and no inline executable content.
- Pin exact D3 modules and build tooling; publish source maps per policy, lockfiles, license
  inventory, SBOM, provenance, reproducible-bundle evidence, and rollback assets.
- Complete an independent review of spec parsing, transforms, rendering, tooltip/annotation text,
  events, exports, workers, lifecycle, and dependency/build boundaries.

## Compatibility and migration

`hedron-charts` cuts `0.2.0` because `ChartSpec` is a substantial new public contract. Existing
beginner components and Matplotlib behavior retain source compatibility. Applications using
Experimental adapters keep explicit imports and opt-in assets. Migration documentation includes:

- current beginner components to `Chart(spec=...)` equivalents;
- Plotly/Altair common cases to typed encodings with a clear unsupported-feature report;
- old event kinds to versioned selection/interaction events;
- theme and CSS overrides to public chart tokens;
- static-only and JavaScript-off deployments;
- rollback to the `hedron-charts` 0.1 line.

Unknown 0.2 fields fail rather than degrade silently. Deprecations name a replacement and removal
window; no 0.1 Experimental backend behavior is promoted accidentally.

## Alternatives considered

### Make Plotly or Vega-Lite the default

Both are capable, but either would make a vendor grammar, bundle, interaction model, and lifecycle
the Hedron contract. They remain valuable adapters. Hedron needs a smaller first-party contract it
can secure, theme, test, and evolve consistently.

### Expose D3 directly

D3 is intentionally low-level and callback-oriented. Direct exposure would make Python typing,
safe serialization, SSR fallback, deterministic diagnostics, and cross-backend conformance much
weaker. D3 remains an internal renderer toolkit.

### Keep static charts as the only Supported path

That preserves safety but cannot meet the product-quality goal for modern analytical applications.
The first-party interactive path must graduate on evidence rather than remain permanently
Experimental.

### Build a canvas-only engine

Canvas helps dense data but is inferior as the universal semantic/debugging/export surface. The
hybrid SVG/Canvas design preserves quality and accessibility while scaling where measurements
justify it.

## Resolved questions (D-066)

### 0.38 definitive

| Question | Answer |
|---|---|
| Element home | **`hedron-chart`** ships in independent Beta **`hedron-charts` `0.2.0`**. It conforms to the public element ABI. **`hedron-elements` stays Alpha** and does **not** depend on charts. Charts may depend on `hedron-core` plus ABI metadata only. |
| Schema | `ChartSpec.schema_version = 1` (JSON schema id **`hedron-chart-spec/1`**). Unknown versions, fields, and operators fail closed with `HED-CHART-*`. Catalogs: [CHART_SPEC.md](../implementation/CHART_SPEC.md). |
| Beginner path | `LineChart` / `AreaChart` / `BarChart` / `ScatterChart` keep current call shapes and compile to `ChartSpec`. Advanced entry is `Chart(spec=...)`. |
| Paint default | **SVG**. Canvas only via inspectable `ChartPlan.renderer` when Stage 1 records a mark threshold **or** the author sets `renderer: canvas`. Paint change must not change scales, identity, accessibility, or export meaning. |
| Workers | **Absent by default.** Add only if `PERF-038` evidence requires them; then bounded, cancellable, and fully disposable. |
| Interaction | Typed versioned `CustomEvent` payloads on stable datum/series keys. Async drill/actions reuse 0.37 **`InteractionState`**; no parallel chart state machine. Hover is never the only path. Selection is not authorization. |
| Human AT | `A11Y-038` requires three-engine automated a11y plus a **scoped** keyboard/AT protocol packet (same honesty as `AT-037` / [#86](https://github.com/eddiethedean/hedron/issues/86)). Do **not** market Supported human AT; do **not** block 0.38 on `SR-021`. |
| D3 candidate set | Pin exact versions in Stage 4, not now: `d3-array`, `d3-scale`, `d3-shape`, `d3-axis`, `d3-selection`, `d3-time`, `d3-time-format`, `d3-format`, `d3-interpolate`, `d3-color`, `d3-brush`, `d3-zoom`, optional `d3-transition` behind reduced-motion. **Not** `d3-geo` / `d3-hierarchy` / `d3-force`. |
| Numeric floors | Keep `VisualizationLimits.max_rows = 10000` and `max_payload_bytes = 1_000_000`. Additional floors live in `chart-capability-inventory-038.toml`. Exact Canvas mark threshold is a Stage 1 lock. |
| Tracking | [#251](https://github.com/eddiethedean/hedron/issues/251) owns every 0.38 gate. Medium remediations: #71/#72 → `RENDER-038`; #75/#81/#201/#239 → `SECURITY-038`; #82 → `A11Y-038`; #83 → `PERF-038`. Issue bodies remain normative; `REGRESS-038` Verified only when they are closed. |

### Later-phase provisional (unblocks Accept; amendable by phase-owned decisions)

| Question | Provisional answer |
|---|---|
| 0.39 chart consumption | DataTable/DataEditor/map/media surfaces consume the 0.38 `hedron-chart` contract rather than a parallel renderer ([#94](https://github.com/eddiethedean/hedron/issues/94)). |
| Whole-platform ABI graduation | Chart-scoped Python/spec/element workflow may be Supported for the locked 0.38 inventory; unrelated tags and the general author ABI remain 0.42. |

## Acceptance

Phase 0.38 requires every row in `release-gate-0.38.toml` Verified with zero Deferred:

- `GRAMMAR-038`, `RENDER-038`, `DESIGN-038`, `VISUAL-038`;
- `INTERACT-038`, `A11Y-038`, `PERF-038`, `EXPORT-038`;
- `SECURITY-038`, `COMPAT-038`, `DOCS-038`, `REGRESS-038`, `PKG-038`.

The exact suites, artifacts, and cut procedure are defined by `RELEASE_0_38.md`,
`HEDRON_CHARTS_038.md`, and `CHART_SPEC.md`.
