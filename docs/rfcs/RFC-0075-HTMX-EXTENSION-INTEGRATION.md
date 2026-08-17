# RFC-0075: First-class HTMX extension integration

**Status:** Accepted<br>
**Target phase:** 0.48 (`v0.48.0`)<br>
**Decision:** D-080<br>
**Stage 0 contract refine:** D-083<br>
**Planning baseline:** Published in-tree `v0.47.0` (D-083; original Stage 0 baseline was Published in-tree `v0.46.0`)<br>
**Required predecessor/cut baseline:** Verified in-tree `v0.47.0`<br>
**Tracking:** [#373](https://github.com/eddiethedean/hedron/issues/373)<br>
**Extends:** RFC-0008, RFC-0009, RFC-0012, RFC-0019, RFC-0021, RFC-0023,
RFC-0024, RFC-0025, RFC-0031, RFC-0032, RFC-0053, RFC-0060, RFC-0070,
RFC-0072, RFC-0073, and RFC-0074

**Revision:** 2026-08-17 — D-083 contract refine against Published in-tree `v0.47.0`:
planning baseline rebased; catalog, asset/activation, SSE/head/preload, and
morph/compat locks recorded; real 0.10 `ExtensionAsset` / `inject_htmx_extensions`
/ SSE / preload / HDJ `ExtensionEvidence` / `safe_hx_swap` seams and 0.43–0.47
handles/catalog/maps lifecycle named. No runtime or version claim.

## Summary

Phase 0.48 turns HTMX extensions from globally shipped but mostly dormant browser assets into an
explicit, typed, demand-driven Hedron capability. Pages and bounded regions declare extensions;
the renderer validates the declaration, injects only pinned assets that are actually needed, emits
the correct `hx-ext` scope, and exposes the result to diagnostics, manifests, adapters, tests, and
Content Security Policy construction.

The phase activates the already bundled SSE and head-support extensions end to end, adds the core
preload extension, and admits Idiomorph only after lifecycle, focus, form, chart, and custom-element
evidence passes. Hedron's existing `InteractionResult`/`HX-Retarget`, OOB, loading, security, and
typed-update contracts remain authoritative; extensions that merely duplicate those contracts are
not added.

## Goals

- Make extension use explicit through a closed `HtmxExtension` catalog and immutable
  `ExtensionSet`, usable from `Page`, components, and HDJ evidence.
- Couple extension declaration, local asset injection, `hx-ext` activation, version/digest/CSP
  metadata, diagnostics, and browser evidence so none can drift independently.
- Replace unconditional extension delivery with deterministic demand-driven injection and preserve
  correct load order after HTMX core under mount prefixes.
- Ship a complete SSE vertical slice for live regions and jobs, including named swaps, event-
  triggered refreshes, terminal close, reconnect, authorization, cleanup, and polling fallback.
- Make head-support useful for registered full-document/boosted navigation and controlled fragment
  assets without allowing arbitrary fragment scripts to escape the asset registry or CSP.
- Add preload for explicitly safe, cacheable GET navigation and fragment requests, integrated with
  the existing `HX-Preloaded` server policy.
- Evaluate and, only with complete evidence, support Idiomorph as an opt-in swap strategy for
  stateful regions.
- Provide extension-aware Explorer, CLI, manifest, conformance, simulation, adapter, security,
  accessibility, performance, and compatibility evidence.

## Non-goals

- Loading every catalog extension, accepting arbitrary CDN URLs, or turning npm packages into an
  ambient plugin system.
- Making SSE, WebSockets, streaming, preload, or browser enhancement a correctness dependency;
  the phase does not supersede the 0.24 `polling_only` production disposition by itself.
- Replacing `InteractionResult`, `StatusPolicy`, `HX-Retarget`, `HX-Reselect`, OOB updates,
  `hx-indicator`, or `hx-disabled-elt` with extension-specific alternatives.
- Adopting `response-targets`, multi-swap, loading-states, HTMX 1 compatibility, arbitrary
  community extensions, client-side templates, JSON encoding, or executable event serialization
  in the initial Supported inventory.
- Exposing unrestricted extension JavaScript hooks, weakening URL/selector/eval validation, or
  scheduling Hedron `1.0`.

## Proposed design

### Declaration and catalog

`HtmxExtension` is a closed identifier for the phase-owned inventory: `sse`, `head-support`,
`preload`, and conditionally `morph`. `ExtensionAsset` remains the source of exact version, digest,
local path, CSP, dependency, and load-order facts. `ExtensionSet` normalizes declarations,
deduplicates them, rejects unknown or incompatible combinations, and produces deterministic
manifest facts.

Pages accept an explicit declaration:

```python
Page(content, htmx_extensions={"sse", "preload"})
```

Typed components such as `SseRegion` may contribute a required extension during render planning.
The final PAGE plan unions explicit and component requirements, injects each local asset once after
HTMX core, and emits a canonical `hx-ext` value at the narrowest valid scope. FRAGMENT responses
never invent executable assets; they carry registered requirements that must be satisfied by the
shell or an authorized head-support flow.

Unknown extensions, missing assets, digest mismatch, invalid dependency order, undeclared
fragment requirements, or a declaration incompatible with the active HTMX major fail closed in
development and produce bounded production diagnostics.

### SSE activation

`SseRegion` renders `hx-ext="sse"`, a validated same-origin `sse-connect`, one or more bounded
`sse-swap` names, optional `sse-close`, and semantic fallback content. `SseTrigger` permits
`hx-trigger="sse:<name>"` to request a server-canonical fragment rather than placing event data
directly into the DOM.

The existing `SseEvent`, `sse_response`, and `job_status_sse_response` paths gain a documented HTML
event contract. Job observation retains bounded polling as Supported fallback. EventSource
authorization, tenant scope, reconnect/`Last-Event-ID`, proxy buffering, connection budgets,
terminal closure, page visibility, DOM removal, swap replacement, and cleanup are tested.

### Head-support activation

`head-support` is enabled only for pages that opt into registered head merging. Eligible responses
contain a controlled `<head>` assembled from `AssetRef` values already admitted by Hedron's asset
and security policies. Unknown inline scripts, event handlers, remote origins, nonce invention,
and unregistered removal are rejected. Merge lifecycle events are observable, and duplicate,
retain, replace, remove, mount-prefix, navigation, rollback, and failure behavior are tested.

### Preload activation

`Preload` is an explicit GET-only authoring value for links and `hx-get` controls. It supports the
extension's bounded initiation modes and maps `HX-Preloaded` to the existing server-side preload
decision helper. Mutation methods, non-idempotent routes, user-derived URLs, responses without an
appropriate private/public cache policy, and unbounded inherited preload scopes fail validation or
remain ordinary non-preloaded interactions.

Performance evidence measures hit rate, wasted bytes, request amplification, origin load, and
perceived navigation latency. Preload remains an optimization and never changes authorization,
CSRF, cache partitioning, response semantics, or availability.

### Idiomorph disposition

The phase vendors no morph asset until a Stage 1 spike passes form value/selection, focus,
`hx-preserve`, Web Component connect/disconnect, chart teardown, OOB, accessibility announcement,
and three-engine lifecycle matrices. If admitted, `morph`, `morph:outerHTML`, and
`morph:innerHTML` enter `safe_hx_swap()` only when `morph` is declared. If the evidence fails,
`MORPH-048` records an explicit Deferred disposition and `morph` is excluded from the release's
Supported inventory; this disposition does not block the rest of 0.48.

### Deliberate exclusions

`response-targets` duplicates server-authoritative status policies and declared-region checks.
Multi-swap duplicates Hedron OOB materialization. Loading-state extensions duplicate typed
indicator/disabled-element behavior. The HTMX WebSocket extension does not match the current typed
page/session channel without a separate wire-protocol RFC. These remain excluded unless a later
RFC identifies a concrete gap and preserves existing authority boundaries.

## Security implications

- All extension assets are pinned, locally served, hashed, licensed, audited, and loaded after the
  compatible HTMX core; no runtime CDN or request-derived asset URL is permitted.
- `sse-connect`, preload destinations, head resources, and extension-introduced selectors pass
  existing safe URL, mount, origin, region, CSP, authorization, and tenant checks.
- Head merging cannot introduce arbitrary executable content or weaken nonce/hash policies.
- SSE event HTML passes the normal renderer and escaping pipeline; event names and close names use
  a closed token grammar and event streams have connection/rate/size/lifetime bounds.
- Extension declarations in HDJ require registered evidence and cannot authorize installation by
  writing `hx-ext` alone.

## Accessibility implications

- SSE and morph updates preserve focus, semantic status/live-region behavior, reduced motion, and
  user control; continuous updates are bounded and pausable where appropriate.
- Preload must not trigger visible state, steal focus, announce content, or make keyboard and touch
  navigation behave differently.
- Head merging preserves title, language, viewport, theme, and accessibility metadata according to
  explicit policy.
- Every enhanced feature retains ordinary links/forms/polling/static content for its required
  task, with scoped automated and keyboard/AT evidence.

## Performance implications

Applications declaring no extension load no extension assets. Each admitted asset has compressed
and uncompressed byte budgets, parse/execute measurements, and no-op cost evidence. SSE includes
connection and reconnect budgets; preload includes amplification and waste budgets; head-support
and morph include merge/swap duration and retained-memory budgets across repeated navigation.

## Testing strategy

- Unit tests for catalog normalization, dependency order, attribute validation, render planning,
  safe swap admission, CSP facts, and deterministic manifests.
- Adapter integration tests for FastAPI, Flask, Django, Posit, and Workbench mount prefixes,
  responses, caching, static assets, and extension absence.
- Chromium, Firefox, and WebKit tests for each vertical slice, progressive enhancement, CSP/no-JS,
  disconnect/reconnect, navigation, focus, reduced motion, cleanup, and failure states.
- Adversarial tests for malicious URLs/selectors/event names/head elements, cross-tenant streams,
  cache confusion, request amplification, asset skew, and unregistered HDJ evidence.
- Packaged example and reference-application coverage using only installed artifacts.

## Compatibility and migration

Existing pages continue to render and use HTMX core unchanged. The currently unconditional SSE and
head-support script injection is deprecated in favor of declarations, with one documented
compatibility window and diagnostics before removal. Existing low-level `hx-ext` markup remains
possible only when matching extension evidence is registered. Polling, OOB, `InteractionResult`,
and all non-extension swaps retain their behavior.

Phase 0.48 targets HTMX 2 (`>=2,<3`). HTMX 4's different extension registration and SSE semantics
are outside this phase and require an explicit future compatibility decision.

## Resolved questions (D-080)

1. **Which extensions?** Closed inventory `sse`, `head-support`, `preload`, and
   conditionally `morph`. `response-targets`, multi-swap, loading-states, HTMX 1,
   WebSocket, CDN/community loaders, client templates, JSON encoding, and executable
   event headers stay excluded.
2. **Demand-driven assets?** Yes. Unused pages load no extension assets once
   declarations replace the 0.10 unconditional PAGE injection, with one documented
   compatibility window.
3. **Live-transport promotion?** No. Completing SSE/preload slices does not supersede
   0.24 `polling_only`.
4. **Morph?** Evidence-gated. `MORPH-048` Verified or an explicit Deferred/excluded
   disposition; unverified morph does not ship.
5. **What is the release baseline?** Verified 0.47 is required before Stage 1 or the
   0.48 cut. Original Stage 0 planning baseline was Published in-tree `v0.46.0`.
   **D-083** rebases the living/planning baseline to Published in-tree `v0.47.0`.

## Resolved questions (D-083)

1. **Does 0.48 still include all 16 gates?** Yes. `EXTENSION-048`, `ASSET-048`,
   `SSE-048`, `HEAD-048`, `PRELOAD-048`, `MORPH-048`, `SECURITY-048`, `A11Y-048`,
   `BROWSER-048`, `PERF-048`, `ADAPTER-048`, `TOOLING-048`, `COMPAT-048`,
   `DOCS-048`, `REGRESS-048`, and `PKG-048` remain in scope. Do not split catalog/assets
   or park morph in a later phase.
2. **Does this refine change 0.49?** No. D-081 still requires Verified 0.48 before
   its Stage 1.
3. **Which shipped seams does 0.48 consume?** `ExtensionAsset` /
   `known_extensions()` / `SSE_EXTENSION_DEFERRED` from
   `hedron_core.htmx_extensions` (pins htmx-ext-sse **2.2.2**,
   htmx-ext-head-support **2.0.2**). PAGE injection via
   `hedron_core.page_assets.inject_htmx_extensions` currently inserts every
   non-deferred known extension after HTMX core. SSE:
   `SseResponse` / `sse_response` / `job_status_sse_response` /
   `extension_script_tags` and `hedron_core.live.SseEvent` / `encode_sse`.
   Preload: `NavigationPreloadPolicy` / `PreloadDecision` / `decide_preload` /
   `HX-Preloaded`. Swap: `safe_hx_swap` does not admit morph;
   `require_supported_swap("morphdom")` stays rejected. HDJ:
   `ExtensionEvidence` with `hx-ext` never installing; tests already use
   `extension_id="sse"`. Interaction stack: `FragmentHandle[BindT, ContentT]`,
   `ActionHandle[InputT, ResultT]`, `BoundFragment[ContentT]`, `Patch[ContentT]`,
   `BaseHandleDescriptor`, `descriptor_fingerprint` (does **not** hash `effect`
   or `extensions`), `TypeSchema` under `hedron.type`,
   `Hedron.include_component` / `include_feature` / `Hedron.interactions`,
   `compile_interaction_catalog` / `seal_app_catalog` after `seal_registry`,
   `InteractionCatalog` / `CatalogEntry` / `PackageProjection`, `FeatureBundle`
   (not an executor), `AppScenario`. Flask/Django remain `projection_adapter`
   stacked on
   [adapter-disposition-044.toml](../acceptance/adapter-disposition-044.toml) and
   [host-portable-facts-045.toml](../acceptance/host-portable-facts-045.toml).
   Morph/browser lifecycle includes `hedron-example`, `hedron-chart`, and 0.47
   `hedron-map`.
4. **Public ids vs asset names?** Closed `HtmxExtension` ids are `sse`,
   `head-support`, `preload`, and conditionally `morph`. `ExtensionAsset.name`
   stays npm-style `htmx-ext-*`. `hx-ext` and HDJ `extension_id` use the public
   id (`sse`, not `htmx-ext-sse`). Lock:
   [htmx-extension-catalog-048.toml](../acceptance/htmx-extension-catalog-048.toml).
5. **Where do symbols live?** Portable catalog/set/plan in `hedron-core` (no
   FastAPI). Additive `Page(..., htmx_extensions=...)` on existing core `Page`.
   `SseRegion` / `SseTrigger` are core HTML components. Preload is a GET-only
   authoring value on links/`hx-get`, not a type named `Preload` (that collides
   with `PreloadDecision`). Flagship/adapters keep calling `inject_page_assets`.
   No new package. HDJ keeps `ExtensionEvidence`; 0.48 projects core catalog
   facts into it.
6. **Compatibility injection?** Cut-day default: PAGE responses with **no**
   explicit declaration and no component requirement still inject the 0.47 pair
   (`sse` + `head-support`) and emit a bounded diagnostic. Explicit empty
   `htmx_extensions=()` opts out (zero extension bytes). Explicit non-empty sets
   are demand-driven only. `preload` / `morph` never ride the default. Removal of
   the default is a later documented train, not the `v0.48.0` cut. Lock:
   [htmx-asset-activation-048.toml](../acceptance/htmx-asset-activation-048.toml).
7. **SSE/preload maturity?** Complete vertical slices do **not** reopen 0.24
   `polling_only`. `SseResponse` / job SSE / `evaluate_preload_request` stay on
   `EXPERIMENTAL_LIVE_SURFACES`. Declared extension assets are Supported-when-pinned;
   APIs stay experimental until a separate live-transport packet. Slice lock:
   [htmx-sse-head-preload-048.toml](../acceptance/htmx-sse-head-preload-048.toml).
8. **Catalog/manifest?** Extension plans are render/CSP/diagnostic facts, **not** a
   new `CatalogEntry.kind`, not a fourth fingerprint, not a `FeatureBundle`
   executor. Optional namespaced `PackageProjection` is allowed; `kind` stays
   `view`/`command`.
9. **Head-support?** Eligible `<head>` merge uses existing `AssetRef` /
   security-policy admission. FRAGMENT still never invents executable assets.
10. **Morph?** Keep `MORPH-048` Planned until a Stage 1 spike covering forms,
    focus, `hx-preserve`, `hedron-example`, `hedron-chart`, **`hedron-map`**,
    OOB, a11y, and three engines. Vendor nothing in Stage 0. Failed spike →
    explicit Deferred/excluded; other gates still cut. Admitted values
    (`morph`, `morph:outerHTML`, `morph:innerHTML`) enter `safe_hx_swap` only
    when `morph` is declared. Lock:
    [htmx-morph-compat-048.toml](../acceptance/htmx-morph-compat-048.toml).
11. **Which diagnostic family?** Keep `HED-HTMX-0001`/`0002` and
    `HED-JINJA-0030`. Reserve `HED-EXT-*` in docs only. Do not assign new
    numbers during this refine.
12. **What does Stage 1 still own?** Numeric limits (asset bytes, SSE
    connections, preload amplification, merge duration, memory), preload.js and
    (if admitted) Idiomorph pins/digests, tracking-issue-bound runtime, and the
    `inject_htmx_extensions` demand-driven implementation. Do not invent those
    numbers here.
13. **HTMX major?** Phase stays HTMX 2 (`>=2,<3`). HTMX 4 is out of scope.
14. **May Stage 1 start before the 0.47 PyPI/Git tag?** Yes for in-tree
    Verified 0.47 evidence. Tracking issue [#373](https://github.com/eddiethedean/hedron/issues/373)
    is bound. Do not wait on `#350` publish assets. Do not start Stage 1 during
    this contract refine.

## Acceptance criteria

- `EXTENSION-048`, `ASSET-048`, `SSE-048`, `HEAD-048`, `PRELOAD-048`, `SECURITY-048`,
  `A11Y-048`, `BROWSER-048`, `PERF-048`, `ADAPTER-048`, `TOOLING-048`, `COMPAT-048`,
  `DOCS-048`, `REGRESS-048`, and `PKG-048` are Verified.
- `MORPH-048` is Verified for an admitted Supported morph extension or records a truthful explicit
  Deferred/excluded disposition; no unverified morph asset or API ships.
- No extension is globally loaded when unused, and declared extensions are activated and usable in
  the packaged reference example.
- The `v0.48.0` cut contains no Deferred row hidden inside a Supported claim.

