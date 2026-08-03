# HTMX acceptance

## Phase 0.2 (`v0.2.0`) subset

- [x] Ordinary navigation yields PAGE documents; `HX-Request: true` yields FRAGMENT responses without duplicating the document shell.
- [x] History restore (`HX-History-Restore-Request: true`) selects PAGE mode.
- [x] The complete HTMX 2 request-header context and approved response headers (`HX-Location`,
  push/replace URL, redirect/refresh, retarget/reselect/reswap, and all trigger timings) are covered;
  external URLs and unsafe CSS selectors are rejected.
- [x] Interaction helpers (`Lazy`, `Poll`, `InfiniteScroll`, `RefreshButton`, `Pagination`, `oob_swap`, `action_attrs`) emit SafeUrl-backed HTMX attrs and validated targets.
- [x] Bundled HTMX is served from `/hedron-static/htmx.min.js` via `Hedron()` or `mount_hedron_static(app)`.
- [x] CSRF for unsafe actions works with HTMX header embedding and form-field tokens.
- [x] Injected HTMX 2 runtime defaults keep `HX-Request` reliable on history misses, enforce
  same-origin/eval/script/CSP policy, and restore native form-validity reporting.

## Later

- [ ] Phase 0.6: browser focus, title, live-region, custom-element lifecycle, OOB, history-miss,
  request-race, and error-fragment conformance.
- [ ] Phase 0.6: typed HTMX request/result/policy envelope with validated primary/OOB swaps, event
  timing, history, status, concurrency, cache behavior, and transparent header/attribute output.
- [ ] Phase 0.6: semantic 422 FastAPI validation fragments plus declared policies for 202, 204,
  401/403, 409, 429, and 5xx responses; non-HTMX requests preserve framework-native JSON.
- [ ] Phase 0.6: authorized declared fragment regions, boosted title/history/full-page fallbacks,
  correct `Vary`/cache keys, synchronized accessible forms/search, and Explorer interaction traces.
- [ ] Phase 0.6: explicit fragment asset/head policy and conformance-gated evaluation of
  `head-support`, Idiomorph, response-targets, and View Transitions.
- [ ] Phase 0.7: cross-adapter HTMX 2 header, DELETE query-parameter, boost/history, 204, 3xx,
  validation, proxy/root-path, and optional transport conformance.
- [ ] Phase 0.7: request-aware URL reversal, disconnect/cancellation propagation, and a 202 job
  contract with bounded polling plus optional SSE promotion.
- [ ] Phase 0.7: independently pinned extension asset contract; evaluate official SSE for jobs and
  keep official WebSockets opt-in for bidirectional use cases.
- [ ] Phase 0.8: Chromium/Firefox/WebKit matrix, core/extension supply-chain audit, history privacy,
  and measured opt-in preload evaluation.
- [ ] Phase 0.8: application/intermediary cache-separation evidence for pages, fragments, history
  restores, and target variants, plus authorization/accessibility/fallback coverage for every
  supported interaction status.

See [HTMX 2 integration audit](../HTMX_2_AUDIT.md) for the feature-by-feature rationale.

## Exit

Phase 0.2 HTMX request/response and helper contracts are covered by FastAPI integration and security suites.
