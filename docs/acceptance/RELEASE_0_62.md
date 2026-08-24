# Release acceptance: 0.62 navigation, optimism, and failure isolation

**Status:** Proposed / Planned gates  
**Implementation:** [NAVIGATION_OPTIMISM_062](../implementation/NAVIGATION_OPTIMISM_062.md)

## Planned contract artifacts

- `interaction-capability-inventory-062.toml`
- `navigation-policy-contract-062.toml`
- `optimistic-risk-inventory-062.toml`
- `failure-identity-contract-062.toml`
- `interaction-browser-disposition-062.toml`
- `interaction-diagnostics-062.toml`
- `interaction-budgets-062.toml`
- `interaction-security-a11y-062.toml`
- `interaction-upgrade-fixtures-062.md`

## Planned gates

| Gate | Requirement | Minimum evidence | Status |
|---|---|---|---|
| `CONTRACT-062` | Navigation, transition, optimism, failure, identity, browser, maturity, and budget contracts are frozen. | Accepted locks validated against 0.61 schemas | Planned |
| `NAV-062` | Navigation preserves canonical URL/title/history/focus/scroll and rejects stale generations. | Native/full/boosted and back-forward browser matrix | Planned |
| `FALLBACK-062` | Script/HTMX/transition/preload absence produces correct ordinary navigation and mutation behavior. | Enhancements-disabled journeys | Planned |
| `PREFETCH-062` | Prefetch is same-origin, safe-method, policy/cache aware, bounded, cancellable, and Progressive. | Security, cache, auth/private, limit, and feature-absent tests | Planned |
| `TRANSITION-062` | Visual transitions are capability-detected, interruption-safe, and reduced-motion aware. | Browser feature/no-feature/motion/cleanup matrix | Planned |
| `OPTIMISM-062` | Only inventoried approved risk classes use optimism with revision, idempotency, confirmation, rollback, and limits. | Risk inventory plus adapter corpus | Planned |
| `CONFLICT-062` | Conflict, permission change, validation failure, timeout, and unknown outcome reconcile safely. | Race/revision/auth/uncertain-outcome tests | Planned |
| `FAILURE-062` | Declared region failures preserve unaffected content and propagate only under locked rules. | Fragment/chart/table/job/element failure matrix | Planned |
| `IDENTITY-062` | Stable keys/targets/writers and bounded schema-compatible transfer are enforced. | Static/runtime diagnostics and replacement races | Planned |
| `DASHBOARD-062` | Coordinated interactions enforce fan-out, cancellation, cache variation, stale, and partial-failure policy. | Reference dashboard end-to-end evidence | Planned |
| `SECURITY-062` | Navigation/optimism cannot grant authority or cross tenant/cache/target boundaries. | CSRF/auth/tenant/replay/redirect/cache adversarial matrix | Planned |
| `A11Y-062` | Focus, announcements, busy/conflict/error recovery, reduced motion, zoom/reflow, and keyboard behavior pass. | Automated plus browser accessibility matrix | Planned |
| `BROWSER-062` | Locked Chromium/Firefox/WebKit versions pass supported and feature-absent paths. | Versioned browser report with screenshots/traces where needed | Planned |
| `PERF-062` | Prefetch, snapshots, optimistic history, patch, fan-out, transition, memory, and cleanup budgets pass. | Baseline/exact/one-over/repeated-operation report | Planned |
| `DOCS-062` | Risk classes, navigation semantics, fallbacks, conflicts, diagnostics, and non-goals are accurate. | Docs/API/example checks | Planned |
| `UPGRADE-062` | Existing full-page/HTMX navigation and `OptimisticMutation` payloads remain compatible and reversible. | Before/after and rollback fixtures | Planned |
| `PKG-062` | Package identity, browser assets, maturity, and reference-app packaged imports agree. | Clean build/install and production-like smoke | Planned |

## Release decision

Release requires all Required rows Verified, exact agreement with the optimistic risk inventory,
zero stale/duplicate/conflict corruption escapes, deterministic cleanup, and correct full navigation
with Progressive features disabled. Excluded high-risk mutations remain server-confirmed.
