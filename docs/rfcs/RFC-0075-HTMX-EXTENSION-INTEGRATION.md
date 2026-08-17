# RFC-0075: First-class HTMX extension integration

**Status:** Accepted<br>
**Target phase:** 0.48 (`v0.48.0`)<br>
**Decision:** D-080<br>
**Planning baseline:** Published in-tree `v0.46.0`<br>
**Required predecessor/cut baseline:** Verified `v0.47.0`<br>
**Extends:** RFC-0008, RFC-0009, RFC-0012, RFC-0019, RFC-0021, RFC-0023,
RFC-0024, RFC-0025, RFC-0031, RFC-0032, RFC-0053, RFC-0060, RFC-0070,
RFC-0072, RFC-0073, and RFC-0074

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

## Acceptance criteria

- `EXTENSION-048`, `ASSET-048`, `SSE-048`, `HEAD-048`, `PRELOAD-048`, `SECURITY-048`,
  `A11Y-048`, `BROWSER-048`, `PERF-048`, `ADAPTER-048`, `TOOLING-048`, `COMPAT-048`,
  `DOCS-048`, `REGRESS-048`, and `PKG-048` are Verified.
- `MORPH-048` is Verified for an admitted Supported morph extension or records a truthful explicit
  Deferred/excluded disposition; no unverified morph asset or API ships.
- No extension is globally loaded when unused, and declared extensions are activated and usable in
  the packaged reference example.
- The `v0.48.0` cut contains no Deferred row hidden inside a Supported claim.

