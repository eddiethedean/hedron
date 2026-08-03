# Security acceptance

## Phase 0.1 (`v0.1.0`) subset

- [x] XSS attempts in text, attributes, URLs, raw HTML, and blocked active tags (`script`/`style`/`iframe`/`srcdoc`/`style` attrs).
- [x] Unsafe URL schemes including encoded/entity smuggling; URL attrs require `SafeUrl` with purpose checks.
- [x] Secret leakage blocked through repr, dump/JSON, identities, and validation messages for secret fields.
- [x] Mass assignment blocked via `extra="forbid"` on Hedron models.
- [ ] CSRF on unsafe cookie-authenticated forms, actions, and editor mutations. *(phase 0.2)*
- [ ] Accidental public addressability and lazy-resource authorization bypass. *(phase 0.2)*
- [ ] Public caching of user, tenant, locale, or permission-sensitive fragments. *(phase 0.2)*
- [ ] Asset traversal, plugin/Explorer abuse, DataEditor forged edits. *(later phases)*
- [ ] Markdown/chart/SVG sanitizer corpus beyond baseline rejection. *(later phases)*

## Release controls

- [ ] Standard and strict profiles have documented headers and CSP behavior. *(phase 0.2+)*
- [ ] CI can emit stable text, JSON, and SARIF diagnostics. *(phase 0.4)*
- [ ] Dependency and component-package audits run in the release pipeline.
- [ ] A maintained threat model records trust boundaries and residual risks.

## Exit

Phase 0.1 core security corpus is green. No critical or high finding remains open for the offline rendering surface.
