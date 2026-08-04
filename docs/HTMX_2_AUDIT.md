# HTMX 2 integration audit

**Status:** Phase 0.6 complete; active plan for phases 0.7–0.8  
**Reviewed:** 2026-08-03  
**Baseline:** HTMX 2.0.10

Hedron treats HTMX as the request-and-swap layer, not as an opaque client runtime. The core
asset is pinned and locally served; optional HTMX extensions are separate, independently
versioned browser assets and are never implied by the core compatibility range.

## Implemented baseline

| HTMX 2 contract | Hedron status |
|---|---|
| Full page versus fragment responses | `HX-Request` selects fragments; history restoration always receives a page. |
| Official request headers | Target, trigger, trigger name, current URL, prompt, boost, and history-restore state are exposed through `HtmxContext`. |
| Official response headers | Location, push/replace URL, redirect, refresh, retarget, reselect, reswap, and all three trigger timings are available through validated helpers. |
| Version-2 attribute surface | Core attributes are serializer-allowed; removed `hx-sse`, `hx-ws`, and non-core `hx-href` are rejected. Executable `hx-on:*` remains outside Hedron's strict-CSP component contract. |
| Version-2 defaults | Same-origin requests are explicit; DELETE URL-parameter behavior and instant scrolling remain HTMX defaults. |
| History | `historyRestoreAsHxRequest` is disabled so `HX-Request` remains a reliable fragment signal; the server still treats `HX-History-Restore-Request` as PAGE defensively. |
| CSP and validation | Eval, response script processing, and injected indicator styles are disabled; native form-validity reporting is enabled. Applications may supply an explicit `htmx-config` meta element to override the complete default profile. |
| OOB and events | OOB helpers and before-swap/after-swap/after-settle response events are supported without hiding the resulting HTML or headers. |
| Browser asset | The bundled file matches the official 2.0.10 SHA-384 digest and requires no Node.js runtime. |

## Phase 0.6 — visualization and browser lifecycle

- Define one typed FastAPI/HTMX interaction boundary: request context plus a result/policy envelope
  for primary content, targets/swaps, OOB updates, event timing, history, status, concurrency, and
  cache behavior. Keep rendered attributes and `HX-*` headers inspectable and directly overrideable.
- Convert FastAPI validation failures to semantic 422 HTML fragments for HTMX actions while
  preserving normal JSON errors for non-HTMX requests. Define accessible handling for 202, 204,
  401, 403, 409, 429, and 5xx responses, including explicit swap/retarget behavior and the known
  loss of HTMX response headers through ordinary 3xx redirects.
- Add route-declared fragment regions. Treat `HX-Target` only as a selector among authorized route
  declarations, never as permission to render arbitrary components. Boosted page fragments retain
  title/history metadata, declared assets, and an independently navigable full-page fallback.
- Make `Vary` and cache keys match actual representation dimensions: page versus fragment, history
  restoration, and target only when the target changes output. Extend cache diagnostics to explain
  each dimension and prevent full-page/fragment cache poisoning.
- Add transparent interaction policies for duplicate-submit/search races (`hx-sync`), disabled
  controls, indicators, `aria-busy`, CSRF, validation focus, and idempotency. Explorer simulates
  request modes and displays primary/OOB destinations, event timing, history, assets, and caching.
- Add real-browser coverage for swap, settle, cleanup, focus, live-region, title, history-miss,
  OOB, and concurrent-request behavior around first-party chart and content adapters.
- Define state-preservation rules for rich custom elements: prefer stable hosts and targeted
  descendant swaps; use `hx-preserve` only where identity and teardown are proven. Evaluate the
  official Idiomorph extension as an opt-in morph strategy, with form state, focus, custom-element
  lifecycle, and accessibility conformance before adoption.
- Define HTMX fragment asset behavior. First-party routes either predeclare required assets in the
  page shell or use an audited, pinned head-update mechanism. Evaluate the official `head-support`
  extension; do not execute arbitrary response scripts or depend on a CDN in production.
- Specify HTML error-fragment handling for 4xx/5xx responses. Prefer explicit core
  `responseHandling` plus validated `HX-Retarget`/`HX-Reselect`; evaluate `response-targets` only
  where declarative status-specific targets materially improve component APIs.
- Evaluate per-swap/global View Transitions as progressive enhancement, gated by
  `prefers-reduced-motion`, focus stability, and browser support.

## Phase 0.7 — adapters, transport, and operations

- Generate component and HTMX URLs through each framework's request-aware reverse router. Verify
  path parameters, mounts, encoding, ASGI `root_path`, proxy prefixes, and external asset hosts;
  do not make stored literal paths part of the portable component contract.
- Propagate browser aborts and superseded requests into server-side disconnect/cancellation checks
  for expensive sources, charts, and jobs. Trace browser abort, timeout, server cancellation, and
  completed-but-discarded work separately.
- Define a 202 job result that renders an accessible bounded-polling status component by default
  and can promote to the official SSE extension without changing the application job contract.
- Expand cross-adapter conformance to all HTMX 2 request and response headers, DELETE query
  parameters, history cache misses, boosted navigation, 204 no-swap responses, validation/error
  fragments, and 3xx header-loss behavior.
- Add an extension asset contract: exact independent versions and digests, local/offline serving,
  CSP declarations, deterministic load order after core HTMX, compatibility tests, and Explorer
  inventory. No extension is bundled merely because it exists.
- Time-box evaluation of the official SSE extension for addressable job/status updates where it
  demonstrably improves on bounded polling. SSE is not required for the 0.7 exit gate and is
  assigned to phase 0.10. WebSocket components share the 0.10 transport gate and still require an
  accepted bidirectional-use-case RFC; never reintroduce removed `hx-sse` or `hx-ws` attributes.
- Cover reverse proxies, root paths, reconnect/backoff, cancellation, cache headers, CSRF, and
  authorization for any selected extension transport.

## Phase 0.8 — release hardening

- Prove cache separation for pages, ordinary fragments, history restores, and declared target
  variants at both application and intermediary boundaries. Exercise every supported interaction
  status with authorization, accessibility, retry, and non-HTMX fallback assertions.
- Run Chromium, Firefox, and WebKit conformance for boost/history, focus, OOB, request races,
  extension teardown, CSP, and reduced-motion behavior.
- Audit the pinned HTMX core and extension assets, recorded digests, licenses, compatibility, and
  upgrade notes. Patch upgrades require the browser suite as well as Python integration tests.
- Verify sensitive pages opt out of history snapshots and that cached snapshots and extension
  diagnostics cannot disclose private content.

## Explicit non-goals through phase 0.9

- Recreating HTMX APIs behind a Python DSL.
- Supporting removed HTMX 1 attributes or the `htmx-1-compat` extension.
- Enabling inline executable attributes, JavaScript-valued headers/values, or response scripts by
  default.
- Bundling every official extension. Core HTML/HTTP mechanisms remain preferred when sufficient.
- Introducing navigation preloading before its phase 0.10 cache/privacy/performance gate.

## Primary sources

- [HTMX 2.0 release](https://htmx.org/posts/2024-06-17-htmx-2-0-0-is-released/)
- [HTMX 1-to-2 migration guide](https://htmx.org/migration-guide-htmx-1/)
- [HTMX documentation](https://htmx.org/docs/)
- [HTMX reference](https://htmx.org/reference/)
- [Official extensions](https://htmx.org/extensions/)
