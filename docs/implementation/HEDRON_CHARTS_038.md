# Phase 0.38 implementation plan: high-fidelity declarative charts

This plan turns [RFC-0069](../rfcs/RFC-0069-HIGH-FIDELITY-CHARTS.md) / D-066 into reviewable
work. The living published tip is `v0.38.0`. Stage 0 (including the post-0.38 contract refine)
adds contracts only and does not change runtime behavior or versions. Tracking
[#251](https://github.com/eddiethedean/hedron/issues/251). Grammar catalogs:
[CHART_SPEC.md](CHART_SPEC.md).

## Outcome

Publish Hedron `v0.38.0` and independent Beta `hedron-charts` `0.2.0` with a Supported first-party
interactive renderer whose visual, interaction, accessibility, performance, export, lifecycle, and
security quality is competitive with bespoke D3 work while remaining declarative and Python-first.

Completion requires every row in
[`release-gate-0.38.toml`](../acceptance/release-gate-0.38.toml) Verified.

## Locked architecture

| Layer | Contract |
|---|---|
| Authoring | Immutable schema-versioned `ChartSpec`; beginner APIs compile to it |
| Compilation | Deterministic `ChartPlan` with transforms, scales, marks, accessibility, renderer decision, assets, warnings, fingerprint |
| Browser | ABI-conforming `hedron-chart`; modular pinned D3; SVG default, Canvas for measured dense cases |
| Static fallback | Semantic figure + reviewed summary/table/export; Matplotlib/SVG for Supported families |
| Interaction | Stable datum/series keys; typed focus/hover/select/brush/zoom/legend/drill intent; no DOM-node payloads |
| Styling | Public chart tokens, light/dark/forced-colors/print, locale/timezone, responsive density |
| Adapters | Matplotlib Supported; Plotly/Altair and other vendor engines explicit Experimental paths |
| Packaging | `hedron-charts` `0.2.0`; prebuilt local assets; no Node requirement for consumers |

## Work breakdown

### Stage 0 — contract and evidence packet (complete)

- Accept D-066 / RFC-0069; lock [Resolved questions (D-066)](../rfcs/RFC-0069-HIGH-FIDELITY-CHARTS.md#resolved-questions-d-066).
- Add this plan, release packet, gate manifest, capability inventory, upgrade fixtures, review
  brief, [production-grade-inventory-038.toml](../acceptance/production-grade-inventory-038.toml),
  [CHART_SPEC.md](CHART_SPEC.md), and scoped [AT-038](../acceptance/human-at/038/PROTOCOL.md).
- Renumber the previously planned Web Component phases to 0.39–0.42 without changing their scope.
- Open tracking [#251](https://github.com/eddiethedean/hedron/issues/251) and bind medium
  remediations #71/#72/#75/#81/#82/#83/#201/#239 to owning gates.
- Rebaseline living published tip to `v0.38.0`.
- Add lenient packet verification to CI.
- Do not modify `hedron-charts` runtime, package versions, living pins, or release status.

**Explicitly forbidden until Stage 1+:** `ChartSpec` / `ChartPlan` / `hedron-chart` / D3 modules in
`packages/`; workspace or `hedron-charts` version bump; flipping any 0.38 gate to Verified;
adopter-facing “0.38 Published” claims.

Exit: `python scripts/verify_pkg_38.py --allow-planned`.

### Stage 1 — baselines and conformance corpus

- Record bundle/render/update/interaction/resize/leak baselines for the current package and selected
  D3 modules on named runners.
- Freeze representative data fixtures: numeric/time/categorical, missing/invalid, long labels,
  locales/timezones, dense series, adversarial strings, and empty/one-row states.
- Establish render-plan JSON schema, browser fixture protocol, screenshot review workflow, and
  static/interactive semantic parity assertions.
- Bind executable tests to every `_gate_038.GATE_TESTS` entry; a gate marked Verified without a
  bound evidence suite fails closed.
- Lock exact thresholds at or tighter than RFC-0069 defaults.

### Stage 2 — `ChartSpec` and compiler (`GRAMMAR-038`)

- Implement typed data, mark, encoding, scale, guide, transform, composition, interaction, theme,
  accessibility, renderer, and export models.
- Validate field/type references and reject executable or unknown constructs.
- Normalize to deterministic `ChartPlan`, stable fingerprints, warnings, and error diagnostics.
- Add JSON schema/version fixtures and clean public exports.

### Stage 3 — scales, layout, and scene model (`DESIGN-038`)

- Implement domains, ticks, formatting, stacking, binning, faceting, legends, label collision,
  annotations, responsive modes, and layout boxes.
- Lock missing/invalid/log/zero/timezone/ordering semantics and misleading-encoding diagnostics.
- Define SVG/Canvas renderer selection from measured plan properties.

### Stage 4 — first-party D3 renderer (`RENDER-038`)

- Build the `hedron-chart` element from pinned modular D3 packages.
- Render the Supported catalog with keyed incremental updates and stable scene identities.
- Implement ResizeObserver/visibility behavior, HTMX lifecycle, failure fallback, and complete
  disconnect cleanup.
- Ship reproducible fingerprinted assets and source maps without a consumer Node dependency.

### Stage 5 — interaction (`INTERACT-038`)

- Implement focus navigation, structured tooltip/inspect, legend filtering, crosshair, selection,
  brush, zoom/pan/reset, and declared drill intent.
- Provide keyboard/pointer/touch parity, reduced-motion behavior, coarse-pointer hit targets, event
  coalescing, and typed bounded payloads.
- Prove ordinary action authz/CSRF boundaries and HTMX swap/history/late-response behavior.

### Stage 6 — accessibility (`A11Y-038`)

- Compile title, description, encoding explanation, summary, annotations, interaction help, and
  bounded tabular/download alternatives.
- Add SVG semantic grouping and Canvas-equivalent HTML navigation without accessibility-tree
  explosions.
- Run three-engine automated a11y and the scoped AT-038 keyboard/AT packet (not Supported
  human AT; do not block on `SR-021`).

### Stage 7 — visual system and gallery (`VISUAL-038`)

- Complete public tokens, palettes, typography, grids, axes, legends, focus, annotations, empty/
  loading/error states, and compact/ordinary/wide responsive compositions.
- Build a reference gallery across chart families, themes, forced colors, print, locales, long
  labels, dense data, and adversarial values.
- Require structural no-clip/no-overlap assertions plus reviewed screenshot changes.

### Stage 8 — performance and dense rendering (`PERF-038`)

- Enforce asset, render, update, interaction, resize, long-task, layout-shift, heap, row/mark/facet,
  transform, and event-rate budgets.
- Implement bounded sampling/aggregation and Canvas fallback with inspectable decisions.
- Add cancellation and worker teardown if workers prove necessary; otherwise keep them absent.

### Stage 9 — export (`EXPORT-038`)

- Implement deterministic SVG, scaled PNG, canonical CSV/JSON, and print export.
- Record schema/theme/locale/timezone/data fingerprints; redact secrets; enforce dimensions and
  authorization; prohibit remote fetches.
- Compare browser/server exports for semantic equivalence.

### Stage 10 — security and supply review (`SECURITY-038`)

- Run schema/transform/prototype-pollution/HTML/URL/SVG/event/export/worker/lifecycle adversarial
  suites.
- Verify strict CSP/Trusted Types and bounded allocation before DOM/Canvas work.
- Complete independent review, dependency licenses, SBOM, provenance, reproducible build, source
  map, vulnerability, and rollback evidence.

### Stage 11 — compatibility, Explorer, and documentation (`COMPAT-038`, `DOCS-038`)

- Preserve beginner component signatures and Matplotlib Supported behavior.
- Publish Plotly/Altair migration reports and keep unsupported backend features explicit.
- Add Explorer spec/plan/data/a11y/perf/theme inspection and failure simulation.
- Publish quickstart, chart catalog, interaction, a11y, theming, performance, export, security,
  migration, troubleshooting, and extension-boundary guides plus packaged examples.

### Stage 12 — cut (`REGRESS-038`, `PKG-038`)

- Run complete Python/browser/visual/a11y/security/perf/package suites.
- Flip all gates to Verified; cut Hedron `v0.38.0` and `hedron-charts` `0.2.0` (**complete**).
- Publish capability inventory, review, benchmark, visual-review, supply, upgrade, and rollback
  artifacts; update living docs only after artifacts exist (**complete** for in-repo evidence).

## Pull-request slicing

No pull request may combine the schema, renderer, full catalog, interaction layer, and package cut.
Recommended slices are: schema/core compiler; individual scale/mark families; layout/guides;
element lifecycle; interaction families; accessibility model; visual system; Canvas/dense path;
exports; Explorer/docs; evidence/cut. Each slice names the gate(s) it advances and includes negative
fixtures.

## Cut commands

During planning and implementation:

```bash
python scripts/verify_pkg_38.py --allow-planned
```

At the `v0.38.0` cut:

```bash
python scripts/verify_pkg_38.py
python scripts/check_release_gate.py 0.38.0 --execute-verified
```
