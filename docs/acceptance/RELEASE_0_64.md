# Release acceptance: 0.64 Hedron HTMX interaction extension

**Status:** Proposed / Planned gates  
**Implementation:** [HTMX_HEDRON_EXTENSION_064](../implementation/HTMX_HEDRON_EXTENSION_064.md)  
**RFC:** [RFC-0091](../rfcs/RFC-0091-HTMX-HEDRON-EXTENSION.md)

## Planned contract artifacts

- `htmx-hedron-extension-contract-064.toml`
- `htmx-hedron-extension-assets-064.toml`
- `htmx-hedron-extension-hosts-064.toml`
- `htmx-hedron-extension-a11y-064.toml`
- `htmx-hedron-extension-trace-064.toml`
- `htmx-hedron-extension-browser-064.toml`
- `htmx-hedron-extension-upgrade-fixtures-064.md`

Names and schemas become authoritative only after Stage 0 acceptance.

## Planned gates

| Gate | Requirement | Minimum evidence | Status |
|---|---|---|---|
| `CONTRACT-064` | Extension id, markers, events, state projection, response facts, and maturity are frozen. | Machine-readable contract locks and schema validation | Planned |
| `ASSET-064` | `htmx-ext-hedron` is pinned, local, digest-checked, licensed, ordered after HTMX core, and demand-loaded. | Asset manifest, CSP/load-order tests, opt-out byte check | Planned |
| `STATE-064` | Browser projection consumes 0.61 lifecycle and operation identity without becoming authoritative. | Native/HTMX/element golden fixtures and spoofing cases | Planned |
| `A11Y-064` | Busy, disabled, announcements, validation focus, keyboard behavior, reduced motion, and no-JS fallback are consistent. | Semantic, keyboard, screen-reader-oriented, and browser evidence | Planned |
| `RACE-064` | Stale, cancelled, superseded, duplicate, removed-target, and reordered responses cannot corrupt current presentation. | Deterministic race corpus across fragment and navigation journeys | Planned |
| `LIFE-064` | Registered modules initialize and teardown exactly once across load, swap, cleanup, OOB, history, and failure paths. | Chart/map/grid/element lifecycle fixtures and leak checks | Planned |
| `TRACE-064` | Browser events, Explorer output, and tests project one bounded redacted trace. | Golden trace parity, truncation, malformed-input, and redaction tests | Planned |
| `INTEGRATE-064` | Hedron page planning, component markers, route metadata, simulator, and package exports agree. | Cross-package render/simulation/integration suite | Planned |
| `CSP-064` | Strict CSP works without inline handlers or response scripts; registry is explicit and scoped. | CSP browser matrix and negative executable-content tests | Planned |
| `BROWSER-064` | Core journeys pass in Chromium, Firefox, and WebKit. | Form, refresh, polling, navigation, focus, OOB, cleanup, and history matrix | Planned |
| `PERF-064` | Extension overhead, metadata, event count, and retained registrations stay within frozen budgets. | Reproducible browser/resource benchmark | Planned |
| `UPGRADE-064` | Pages without the declaration retain pre-extension behavior and rollback is documented. | Before/after fixtures, absent-asset tests, migration/rollback docs | Planned |
| `DOCS-064` | API, recipes, security model, fallback behavior, diagnostics, and extension declaration are accurate. | Docs link/API/example checks and rendered guide | Planned |
| `PKG-064` | Clean packages expose identical extension metadata and locally serve the asset. | Build/install/package identity and production-like smoke | Planned |

## Release decision

Release requires every Required row Verified, zero Deferred Required capabilities, the extension
absent-path fallback passing, no client-side authority or inline-script escape hatch, and signed-off
asset, compatibility, accessibility, browser, performance, and rollback evidence. Progressive and
Experimental consumers retain their labels in docs, Explorer, metadata, and package manifests.
