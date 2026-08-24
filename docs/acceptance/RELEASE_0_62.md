# Release acceptance: 0.62 navigation, optimism, and failure isolation

**Status:** Verified in tree; release candidate ready for `v0.62.0`
**Implementation:** [NAVIGATION_OPTIMISM_062](../implementation/NAVIGATION_OPTIMISM_062.md)

## Contract artifacts

- `interaction-capability-inventory-062.toml`
- `navigation-policy-contract-062.toml`
- `optimistic-risk-inventory-062.toml`
- `failure-identity-contract-062.toml`
- `interaction-browser-disposition-062.toml`
- `interaction-diagnostics-062.toml`
- `interaction-budgets-062.toml`
- `interaction-security-a11y-062.toml`
- `interaction-upgrade-fixtures-062.md`

## Verified gates

| Gate | Maturity | Requirement | Minimum evidence | Status |
|---|---|---|---|---|
| `CONTRACT-062` | Required | Navigation, optimism, failure, identity, maturity, and budget contracts are frozen without redefining 0.61 schemas. | Accepted locks validated against 0.61 schemas | Verified |
| `NAV-062` | Required | Navigation preserves canonical URL/title/history/focus/scroll and rejects stale generations. | Native/full and back-forward browser matrix | Verified |
| `FALLBACK-062` | Required | Script/HTMX/transition/preload absence produces correct ordinary navigation and mutation behavior. | Enhancements-disabled journeys | Verified |
| `PREFETCH-062` | Progressive | If shipped, prefetch is same-origin, safe-method, policy/cache aware, bounded, cancellable, and observable. | Security, cache, auth/private, limit, and feature-absent tests | Verified |
| `TRANSITION-062` | Progressive | If shipped, visual transitions are capability-detected, interruption-safe, and reduced-motion aware. | Browser feature/no-feature/motion/cleanup matrix | Verified |
| `OPTIMISM-062` | Required | Only approved reversible risk classes use optimism with revision, idempotency, confirmation, rollback, and limits. | Risk inventory plus toggle/scalar/DataEditor corpus | Verified |
| `CONFLICT-062` | Required | Conflict, permission change, validation failure, timeout, and unknown outcome reconcile safely. | Race/revision/auth/uncertain-outcome tests | Verified |
| `FAILURE-062` | Required | Declared region failures preserve unaffected content and propagate only under locked rules. | Fragment/chart/table/job/element failure matrix | Verified |
| `IDENTITY-062` | Required | Stable keys/targets/writers and bounded schema-compatible transfer are enforced. | Static/runtime diagnostics and replacement races | Verified |
| `DASHBOARD-062` | Progressive | Coordinated fan-out remains explicitly outside the 0.62 Supported claim. | No dashboard fan-out shipped; omission recorded in the release gate | Omitted |
| `SECURITY-062` | Required | Navigation/optimism cannot grant authority or cross tenant/cache/target boundaries. | CSRF/auth/tenant/replay/redirect/cache adversarial matrix | Verified |
| `A11Y-062` | Required | Focus, announcements, busy/conflict/error recovery, reduced motion, zoom/reflow, and keyboard behavior pass. | Automated plus browser accessibility matrix | Verified |
| `BROWSER-062` | Required | Locked Chromium/Firefox/WebKit versions pass Required and feature-absent paths. | Versioned browser report with screenshots/traces where needed | Verified |
| `PERF-062` | Required | Required navigation, optimistic core, failure, memory, and cleanup budgets pass; Progressive budgets are reported when shipped. | Baseline/exact/one-over/repeated-operation report | Verified |
| `DOCS-062` | Required | Risk classes, navigation semantics, fallbacks, conflicts, diagnostics, and non-goals are accurate. | Docs/API/example checks | Verified |
| `UPGRADE-062` | Required | Existing full-page/HTMX navigation and `OptimisticMutation` payloads remain compatible and reversible. | Before/after and rollback fixtures | Verified |
| `PKG-062` | Required | Package identity, maturity, and reference-app packaged imports agree. | Clean build/install and production-like smoke | Verified |

## Release decision

Release requires all Required rows Verified, exact agreement with the optimistic risk inventory,
zero stale/duplicate/conflict corruption escapes, deterministic cleanup, and correct full navigation
with Progressive features disabled. Each Progressive row must either be Verified with its fallback
evidence or explicitly omitted from the release notes and availability inventory. Excluded high-risk
mutations remain server-confirmed.
