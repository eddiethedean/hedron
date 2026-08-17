# HTMX extension integration implementation plan (phase 0.48)

**Status:** Planned; Stage 0 contract refined by D-083 against Published in-tree `v0.47.0`<br>
**Tracking:** [#373](https://github.com/eddiethedean/hedron/issues/373)<br>
**Decision/RFC:** D-080, refined by D-083 / [RFC-0075](../rfcs/RFC-0075-HTMX-EXTENSION-INTEGRATION.md)<br>
**Planning baseline:** Published in-tree `v0.47.0`<br>
**Target:** Hedron `v0.48.0`<br>
**Required predecessor:** Verified `v0.47.0`

D-083 does not authorize Stage 1. It names shipped seams `ExtensionAsset`,
`known_extensions()`, `inject_htmx_extensions`, `SseResponse` /
`job_status_sse_response`, `decide_preload` / `HX-Preloaded`, HDJ
`ExtensionEvidence`, `safe_hx_swap`, and 0.43–0.47 handles/catalog/maps
lifecycle. `Page.htmx_extensions`, `HtmxExtension`, `ExtensionSet`,
`SseRegion`, and `SseTrigger` remain unimplemented until Stage 1.

## Consume shipped, do not fork

- `hedron_core.htmx_extensions.ExtensionAsset` / `known_extensions()` /
  `SSE_EXTENSION_DEFERRED`. Current pins: **htmx-ext-sse 2.2.2**,
  **htmx-ext-head-support 2.0.2**. HTMX core remains 2.0.10.
- `hedron_core.page_assets.inject_htmx_extensions` / `inject_page_assets`: PAGE
  currently injects every non-deferred known extension after HTMX core. That is
  the COMPAT-048 compatibility default, not a third injector.
- `hedron.experimental` SSE helpers: `SseResponse`, `sse_response`,
  `job_status_sse_response`, `extension_script_tags`. Framing:
  `hedron_core.live.SseEvent` / `encode_sse`.
- `hedron_core.preload.NavigationPreloadPolicy` / `PreloadDecision` /
  `decide_preload` and `HX-Preloaded`. Flagship helpers stay on
  `EXPERIMENTAL_LIVE_SURFACES`.
- `hedron_core.htmx_contract.safe_hx_swap`: morph is **not** admitted. Sim
  `require_supported_swap("morphdom")` stays rejected until `MORPH-048`.
- HDJ `ExtensionEvidence` / `ExtensionRegistry`: `hx-ext` never installs;
  tests already use `extension_id="sse"` and `htmx.extension:<id>` features.
- 0.43–0.46 handles, `TypeSchema` under `hedron.type`, `InteractionCatalog` /
  `PackageProjection`, `FeatureBundle` (not an executor). Flask/Django remain
  `projection_adapter`.
- Web Component HTMX swap-dispose: `hedron-example`, `hedron-chart`, and 0.47
  `hedron-map`. Do **not** reopen maps or charts.

Lock files: [htmx-extension-catalog-048.toml](../acceptance/htmx-extension-catalog-048.toml),
[htmx-asset-activation-048.toml](../acceptance/htmx-asset-activation-048.toml),
[htmx-sse-head-preload-048.toml](../acceptance/htmx-sse-head-preload-048.toml),
[htmx-morph-compat-048.toml](../acceptance/htmx-morph-compat-048.toml).

## Architecture

One-way layers; no new package:

1. **Portable catalog:** `HtmxExtension`, `ExtensionSet`, existing
   `ExtensionAsset` facts in `hedron-core` (no FastAPI).
2. **Render planning:** `Page.htmx_extensions` unions explicit and component
   requirements, injects local assets once after HTMX core, emits `hx-ext`.
3. **Typed slices:** `SseRegion` / `SseTrigger` in core; GET preload as an
   authoring value on links/`hx-get` (not a type named `Preload`).
4. **Host adapters:** FastAPI/Flask/Django/Posit/Workbench keep calling
   `inject_page_assets` with mount-prefix rewriting.
5. **Evidence:** Explorer/CLI/manifest/scenario/conformance/HDJ consume the
   same plan facts; they never become runtime authority.

HDJ keeps `ExtensionEvidence`. 0.48 projects core catalog facts into that
registry; it does not replace Jinja types.

## Work packages

### M1 — Catalog and declaration

- Add closed `HtmxExtension` ids `sse`, `head-support`, `preload`, and
  conditional `morph`.
- Keep `ExtensionAsset.name` as `htmx-ext-*`. Emit `hx-ext` and HDJ
  `extension_id` as the public id.
- Add immutable `ExtensionSet` normalization, unknown/conflict failure, and
  deterministic manifest facts.
- Add additive `Page(..., htmx_extensions=...)`. Unset keeps the 0.47
  compatibility default; empty opts out; non-empty is demand-driven.
- Project catalog facts into HDJ `ExtensionEvidence` without forking
  `HED-JINJA-0030`.

### M2 — Demand-driven assets

- Change `inject_htmx_extensions` to accept a declared set instead of every
  non-deferred pin.
- Preserve load order after HTMX core, mount prefixes, CSP facts, digests,
  licenses, and dedupe.
- Implement the compatibility default (`sse` + `head-support`) plus diagnostic.
- Never implicit-inject `preload` or `morph`.
- Prove zero extension bytes on explicit opt-out.

### M3 — SSE vertical slice

- Add `SseRegion` / `SseTrigger` over existing `SseEvent` / `sse_response` /
  `job_status_sse_response`.
- Validate `sse-connect`, closed `sse-swap` / `sse-close` tokens, reconnect /
  `Last-Event-ID`, terminal close, auth/tenant/connection bounds, cleanup.
- Keep polling as the Supported fallback. Do not remove helpers from
  `EXPERIMENTAL_LIVE_SURFACES`.

### M4 — Head-support vertical slice

- Enable `head-support` only for pages that opt into registered head merging.
- Merge controlled `<head>` from admitted `AssetRef` values. Reject unknown
  inline scripts, event handlers, remote origins, nonce invention, and
  unregistered removal.
- FRAGMENT responses still never invent executable assets.

### M5 — Preload vertical slice

- Add a GET-only authoring value with closed initiation modes `mousedown`,
  `mouseover`, and `touchstart`.
- Map `HX-Preloaded` onto existing `decide_preload`. Reject mutation methods,
  user-derived URLs, and unbounded inherited scopes.
- Keep preload APIs experimental. Preload remains an optimization.

### M6 — Idiomorph admission spike

- Vendor **no** morph asset in Stage 0.
- Stage 1 spike: forms/focus/`hx-preserve`, `hedron-example`, `hedron-chart`,
  `hedron-map`, OOB, a11y announcement, Chromium/Firefox/WebKit.
- On pass: admit `morph` / `morph:outerHTML` / `morph:innerHTML` in
  `safe_hx_swap` only when declared.
- On fail: `MORPH-048` Deferred/excluded; other gates may still cut.

### M7 — Security, accessibility, browser, performance

- Safe URL, origin, selector, event-name, head, stream, cache, CSP, and HDJ
  boundaries. Keep `HED-HTMX-0001` / `0002`. Reserve `HED-EXT-*` in docs only.
- Semantic fallbacks, focus, live regions, pause/control, reduced motion,
  keyboard/touch parity, head metadata. Scoped AT honesty; do not close
  `SR-021`.
- Three-engine activation/failure/reconnect/navigation/race/cancel/cleanup.
- Measure asset bytes, parse/execute, SSE connection/reconnect, preload
  amplification, head/morph duration, and retained memory. Stage 0 names
  knobs only.

### M8 — Adapters, tooling, docs, packaging

- FastAPI/Flask/Django/Posit/Workbench static paths, mounts, CSP, caching,
  streaming capability labels, and absence.
- Explorer, CLI, manifest, scenario, conformance, simulation, diagnostics,
  and static HDJ inspection without executing untrusted code.
- Packaged reference example that exercises every admitted extension and its
  fallback.
- Upgrade fixtures from Verified `v0.47.0`. Clean wheel/sdist, licenses,
  SBOM, provenance, Python/browser matrices.

## Failure and diagnostic families

Reserve documentation namespace `HED-EXT-*`. Existing `HED-HTMX-0001`,
`HED-HTMX-0002`, and `HED-JINJA-0030` remain compatible. Exact new code
numbers are assigned only with implementation and error-code documentation.

## Stage ordering

- **Stage 0:** accepted contracts, complete planning packet, D-083
  consume-shipped locks, no runtime/version claim.
- **Stage 1:** after Verified 0.47 and [#373](https://github.com/eddiethedean/hedron/issues/373); measure baselines and
  implement M1–M2. Do not start Stage 1 during the D-083 contract refine. Do
  not block Stage 1 on PyPI/`#350` publish assets.
- **Stage 2:** M3–M6 vertical slices and morph spike.
- **Stage 3:** M7–M8 whole-matrix evidence, docs, package/release rehearsal.
- **Cut:** every non-disposition 0.48 row Verified; `MORPH-048` Verified or
  explicitly Deferred/excluded. Do not tag `v0.48.0` from Stage 0.

## Non-goals

- No new distribution, no CDN/community extension loader, no HTMX 1 or HTMX 4.
- No `response-targets`, multi-swap, loading-states, or WebSocket extension.
- No live-transport promotion, `polling_only` reopen, `SR-021` closure, or `1.0`.
- No Stage 0 `Page.htmx_extensions` runtime, preload.js vendoring, or Idiomorph
  vendoring.
