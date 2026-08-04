# Security acceptance

## Phase 0.1 (`v0.1.0`) subset

- [x] XSS attempts in text, attributes, URLs, raw HTML, and blocked active tags (`script`/`style`/`iframe`/`srcdoc`/`style` attrs).
- [x] Unsafe URL schemes including encoded/entity smuggling; URL attrs require `SafeUrl` with purpose checks (including `srcset`, `ping`, `hx-push-url`, and `hx-replace-url`).
- [x] Secret leakage blocked through repr, dump/JSON, identities, and validation messages for secret fields; `Secret[T]` validates the inner type `T`.
- [x] Mass assignment blocked via `extra="forbid"` on Hedron models.

## Phase 0.2 (`v0.2.0`) subset

- [x] CSRF on unsafe actions: cookie is reused across GETs (not rotated per response); header `X-CSRF-Token` and form field `csrf_token` both validate against the cookie.
- [x] Accidental public addressability and lazy-resource authorization bypass (addressables require `include_component` + caller dependencies).
- [x] Private authenticated caching: when `request.state.hedron_authenticated` is set, responses include `Cache-Control: private, no-store`.
- [x] Safe redirects: `redirect_local` rejects externals; `redirect_external` is denied unless `allow_external_redirects=True`, and only `http`/`https` URLs are accepted.
- [x] Approved HTMX response headers (`HX-Redirect`, `HX-Push-Url`, `HX-Location`) require local
  paths even when supplied through generic interaction header mappings.
  *(`SEC-C06-001` / `tests/security/test_interaction_headers.py`)*
- [x] CSS/asset URL traversal, symlink escape, remote fetch, and missing assets are rejected. *(phase 0.3 scoped styles / asset pipeline)*
- [x] DataEditor forged edits (read-only/hidden/unauthorized fields and unauthorized deletes) rejected server-side. *(phase 0.5)*
- [ ] Plugin/Explorer abuse corpus beyond default guards. *(later phases)*
- [x] Markdown/chart/SVG sanitizer corpus covers fallback interpolation and SVG event/active-content
  attributes beyond script-tag checks.
  *(`SEC-C06-002` / `tests/security/test_chart_svg_corpus.py`)*

## Release controls

- [x] Standard and strict profiles have documented headers and CSP behavior. *(phase 0.2+)*
- [x] Strict profile requires an explicit `session_secret` (default development secret is rejected).
- [x] CI can emit stable text, JSON, and SARIF diagnostics. *(phase 0.4 — `hedron check`)*
- [x] Dependency and component-package audits run in the release pipeline.
  *(`SEC-08-002` / `scripts/dep_audit.py` + evidence bundle)*
- [x] A maintained threat model records trust boundaries and residual risks.
  *(`SEC-08-001` / [threat-model.md](../guides/threat-model.md))*
- [x] Browser-asset pin and digest audit for bundled HTMX.
  *(`SEC-08-003` / `scripts/asset_audit.py`)*

## Exit

Phase 0.1 core security corpus is green. Phase 0.2 CSRF, redirect, cache, and HTMX header suites pass. No critical or high finding remains open for the offline rendering surface or the FastAPI MVP security path.
