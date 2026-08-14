# Hedron `v0.38` high-fidelity charts acceptance

**Status:** Planned (Stage 0 packet refined). Living published tip is **`v0.37.0`**; phase
0.37 is Published and 0.38 implementation may begin.

Phase 0.38 makes an ABI-conforming **`hedron-chart` Web Component** the first-party interactive
default for `hedron-charts` `0.2.0`. Its typed grammar, rendering quality, interaction,
accessibility, responsive behavior, export, performance, security, and lifecycle are release-gated
at a D3-class quality bar. Evidence is indexed by
[`release-gate-0.38.toml`](release-gate-0.38.toml). **Zero Deferred:** every 0.38-owned row must be
Verified at cut.

Owning decision: [D-066](../DECISIONS.md). Design:
[RFC-0069](../rfcs/RFC-0069-HIGH-FIDELITY-CHARTS.md) (**Accepted**). Implementation:
[HEDRON_CHARTS_038](../implementation/HEDRON_CHARTS_038.md). Capability inventory:
[`chart-capability-inventory-038.toml`](chart-capability-inventory-038.toml).

## Release contract at cut

- Coordinated Hedron train: `v0.38.0`.
- Independent Beta package: **`hedron-charts` `0.2.0`**, compatible with the 0.38 core train.
- First-party element: **`hedron-chart`**, conforming to the public element ABI without making
  `hedron-elements` production-grade before 0.42.
- Public advanced API: `Chart`, `ChartSpec`, `ChartPlan`, typed marks/encodings/scales/transforms/
  interactions/themes/exports, and versioned diagnostics/events.
- Existing `LineChart`, `AreaChart`, `BarChart`, and `ScatterChart` signatures remain compatible and
  compile to the new grammar.
- Matplotlib remains Supported. Plotly, Altair/Vega-Lite, ECharts, Chart.js, and other vendor
  backends remain explicit Experimental adapters unless separately graduated.
- Browser evidence: Chromium, Firefox, and WebKit on recorded exact versions.
- Python applications consume prebuilt local assets; Node.js and a bundler are maintainer build
  tools, not application dependencies.

## Exact cut matrix

| Lane | Required proof | Command |
|---|---|---|
| Grammar/compiler | Typed schema, normalization, transforms, inference, diagnostics, fingerprints | `check_grammar_038.py` |
| Renderer/catalog | `hedron-chart`, modular D3, SVG/Canvas, Supported family corpus, lifecycle | `check_render_038.py` |
| Design system | Scales, axes, legends, labels, annotations, themes, locale, responsive layout | `check_design_038.py` |
| Visual review | Multi-viewport/theme/locale gallery, no clipping/overlap, reviewed goldens | `check_visual_038.py` |
| Interaction | Keyboard/pointer/touch inspect, select, brush, zoom, legend, drill intent, HTMX | `check_interact_038.py` |
| Accessibility | Semantic SVG/Canvas layer, summaries/tables, forced colors, AT workflows | `check_a11y_038.py` |
| Performance | Assets, 1k/10k rendering, update/resize/input, long tasks, leaks, bounds | `check_perf_038.py` |
| Export | Deterministic SVG/PNG/CSV/JSON/print, authorization, metadata, parity | `check_export_038.py` |
| Security | Spec/transform/text/URL/SVG/event/export/worker/lifecycle review and adversarial suite | `check_security_038.py` |
| Compatibility | Beginner APIs, Matplotlib, vendor opt-ins, 0.1 migration/rollback, browsers | `check_compat_038.py` |
| Documentation | Catalog, cookbook, Explorer, a11y, performance, export, migration, examples | `check_docs_038.py` |
| Regression | Full Python/browser/visual/a11y/security/performance suite | `check_regress_038.py` |
| Packaging | Wheels/assets/types, supply evidence, inventory, release rehearsal | `verify_pkg_38.py` |

## Locked acceptance criteria

### Grammar and semantic correctness

- [ ] `ChartSpec` and `ChartPlan` have versioned JSON schemas, typed Python APIs, stable fixtures,
  deterministic serialization/fingerprints, and forward/unknown-version failure behavior.
- [ ] Every field, mark, encoding, scale, transform, composition, interaction, theme, and export
  option is allowlisted and bounded; no JavaScript callback or open expression channel exists.
- [ ] Missing/invalid/infinite data, duplicate identities, log-domain violations, bar zero baseline,
  timezone ambiguity, ordering, stacking, and empty/one-row cases have tested dispositions.
- [ ] Compiler inference is visible in `ChartPlan` and Explorer; explicitly supplied values win or
  fail clearly rather than being silently rewritten.

### Rendering and visual quality

- [ ] Supported catalog: line/area, bar/grouped/stacked/diverging/waterfall/bullet, scatter/bubble,
  histogram/density/box/strip, heatmap, OHLC/candlestick, bounded pie/donut, layers, facets,
  annotations, and reference lines/bands.
- [ ] SVG/Canvas renderer choice is deterministic and inspectable; paint-surface changes preserve
  scales, data meaning, identity, interactions, accessibility, and export meaning.
- [ ] Compact, normal, and wide layouts have deliberate tick/label/legend/facet density and no
  fixture clipping, overflow, accidental overlap, or unreadable hit targets.
- [ ] Light, dark, forced-color, high-contrast, reduced-motion, print, locale/timezone, long-label,
  empty/loading/error, and invalid-data visual states have reviewed fixtures.
- [ ] Golden updates include review metadata and before/after artifacts; the check rejects
  unreviewed bulk snapshot replacement.

### Web Component lifecycle and interaction

- [ ] `hedron-chart` upgrades useful semantic fallback and survives connect/reconnect/disconnect,
  resize, hidden/revealed containers, inner/outer/OOB HTMX swaps, history restore, and module failure.
- [ ] Stable datum/series keys drive keyed updates and events; no public payload contains DOM nodes,
  arbitrary selectors, raw HTML, callbacks, or authorization state.
- [ ] Inspect/tooltip, focus navigation, legend filtering, point/range selection, brush,
  zoom/pan/reset, crosshair, and drill intent have keyboard/pointer/touch/reduced-motion coverage.
- [ ] One hundred mount/update/disconnect cycles leave zero registered chart instances, workers,
  observers, listeners, timers, object URLs, or material retained heap beyond measured noise.

### Accessibility

- [ ] Every chart has title and purpose/description plus a compiled encoding explanation, bounded
  summary/table/download alternative, annotations, and interaction help.
- [ ] SVG exposes meaningful groups without flooding the accessibility tree; Canvas retains an
  equivalent HTML interaction model and does not hide unique data behind pixels.
- [ ] Hover is never the only path. Focus is visible and stable across update/resize/HTMX; forced
  colors and 200%/400% zoom/reflow remain usable.
- [ ] Three-engine automated evidence and representative keyboard/screen-reader sessions cover
  inspect, series navigation, selection, legend filter, zoom reset, annotations, and fallback.

### Performance and loading

- [ ] Core renderer bundle is at most 90 KiB gzip; all first-party 0.38 chunks used by the gallery
  total at most 160 KiB gzip; routes without charts load zero chart bytes.
- [ ] On the recorded Chromium CI runner: 1,000 marks initial p95 ≤150 ms, update p95 ≤75 ms;
  10,000-mark dense p95 ≤400 ms with no task >150 ms; inspect p95 ≤50 ms; resize p95 ≤100 ms.
- [ ] Row, field, transform, facet, mark, label, payload, export, worker-memory, and event-rate
  budgets fail before unbounded allocation/DOM creation.
- [ ] Dense paths document whether they aggregate, sample, or use Canvas; no silent point loss.

### Export, security, and supply

- [ ] SVG, scale-aware PNG, canonical CSV/JSON, and print exports are deterministic, bounded,
  authorized, metadata-bearing, secret-safe, and remote-fetch-free.
- [ ] Strict CSP/Trusted Types passes without `unsafe-eval`, inline executable content, remote
  runtimes/data, active SVG, or raw-HTML tooltips/annotations.
- [ ] Independent review resolves all critical/high findings across parsing, transforms, paint,
  events, exports, workers, lifecycle, and build dependencies.
- [ ] Exact D3 modules/tooling, reproducible bundles, source maps, licenses, SBOM, provenance,
  vulnerability disposition, retained artifacts, and rollback assets are published.

### Compatibility and documentation

- [ ] Existing beginner APIs and Matplotlib Supported behavior pass source/render migration tests.
- [ ] Plotly/Altair common-case migration reports identify converted and unsupported features; no
  Experimental adapter becomes an implicit default.
- [ ] Explorer shows spec, normalized plan, data/transform counts, renderer choice, accessibility,
  events, performance, assets, diagnostics, and theme/viewport/failure previews.
- [ ] Public docs include quickstart, catalog, grammar, interactions, a11y, theming, responsive
  design, performance, exports, security, migration/rollback, troubleshooting, and packaged apps.

## Stage 0 entry/exit

- [x] D-066 Accepted and RFC-0069 Accepted
- [x] Phase 0.38 inserted; previous planned 0.38–0.41 phases re-homed to 0.39–0.42
- [x] Gate manifest, implementation plan, capability inventory, upgrade fixture, and review brief
  exist
- [ ] Tracking issue is opened and bound to every 0.38 gate before Stage 1 implementation
- [ ] `v0.37.0` is published before runtime implementation begins
- [x] Stage 0 makes no runtime/version/living-tip claim

## Verification

During planning:

```bash
python scripts/verify_pkg_38.py --allow-planned
```

At cut:

```bash
python scripts/verify_pkg_38.py
python scripts/check_release_gate.py 0.38.0 --execute-verified
```
