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

- [x] Phase 0.6 closure (`HTMX-C06-003`): Chromium Playwright smoke for fragment swap + OOB
  (`HEDRON_BROWSER=1 pytest -m browser`; CI job `browser`). Focus/title/CE teardown matrix remains
  0.8 depth.
- [x] Phase 0.6 closure (`HTMX-C06-001` / `HTMX-C06-002`): typed `InteractionResult` envelope
  revalidates header mappings; OOB + declared fragment regions + `Vary`/cache hints + Explorer
  traces covered by `tests/security/test_interaction_headers.py` and `tests/unit/test_phase06.py`.
- [x] Phase 0.6: semantic 422 FastAPI validation fragments plus declared policies for 202, 204,
  401/403, 409, 429, and 5xx responses; non-HTMX requests preserve framework-native JSON.
- [x] Phase 0.6: explicit fragment asset/head policy and conformance-gated evaluation of
  `head-support`, Idiomorph, response-targets, and View Transitions.
- [ ] Phase 0.7: cross-adapter HTMX 2 header, DELETE query-parameter, boost/history, 204, 3xx,
  validation, proxy/root-path, and optional transport conformance.
- [ ] Phase 0.7: request-aware URL reversal, disconnect/cancellation propagation, and a 202 job
  contract with bounded polling plus optional SSE promotion.
- [ ] Phase 0.7: independently pinned extension asset contract and a time-boxed official SSE
  decision for jobs. Polling is the required baseline; SSE may remain deferred and WebSocket
  components remain assigned to phase 0.10 and require an accepted transport RFC.
- [x] Phase 0.8: Chromium/Firefox/WebKit matrix, core/extension supply-chain audit, and history privacy.
  *(`HTMX-08-001` / `HTMX-08-002` / `SEC-08-003`; CI browser matrix)*
- [x] Phase 0.8: application/intermediary cache-separation evidence for pages, fragments, history
  restores, and target variants, plus authorization/accessibility/fallback coverage for every
  supported interaction status.
  *(`HTMX-08-003` / `tests/unit/test_htmx_cache_matrix.py`)*

See [HTMX 2 integration audit](../HTMX_2_AUDIT.md) and [release-gate-0.6.toml](release-gate-0.6.toml).

## Exit

Phase 0.2 HTMX request/response and helper contracts are covered by FastAPI integration and security suites.
Phase 0.6 closure IDs above are `Verified` under [EVIDENCE.md](EVIDENCE.md).
