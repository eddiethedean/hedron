# Release acceptance: 0.61 action state and async boundaries

**Status:** Implementation baseline complete / release evidence pending
**Implementation:** [ACTION_STATE_ASYNC_061](../implementation/ACTION_STATE_ASYNC_061.md)

## Planned contract artifacts

- `interaction-capability-inventory-061.toml`
- `action-state-contract-061.toml`
- `async-region-contract-061.toml`
- `interaction-host-disposition-061.toml`
- `interaction-trace-schema-061.toml`
- `interaction-diagnostics-061.toml`
- `interaction-budgets-061.toml`
- `interaction-security-a11y-061.toml`
- `interaction-upgrade-fixtures-061.md`
- `phase061-surface-contract.toml`

Names and schemas become authoritative only after Stage 0 acceptance.

## Planned gates

| Gate | Requirement | Minimum evidence | Status |
|---|---|---|---|
| `CONTRACT-061` | Lifecycle, operation, policy, boundary, trace, maturity, host, and budget contracts are frozen and cross-linked. | Accepted machine-readable locks and schema validation | Planned |
| `ACTIONSTATE-061` | All Required adapters project the same typed lifecycle without replacing existing state authority. | Core transition corpus and cross-adapter golden fixtures | Planned |
| `OPERATION-061` | Operation identity, generation, target, correlation, and revision rules are stable and non-authoritative. | Identity/property tests and spoofing cases | Planned |
| `ASYNC-061` | Async regions cover initial, pending, empty, success, timeout, cancelled, error, retry, and ordinary fallback. | Render, HTTP, fragment, polling/HTMX, and browser journeys | Planned |
| `SURFACE-061` | #668–#672 expose additive, finite, server-rendered surface contracts with shared CSS parity. | Public import, render marker, CSS parity, responsive/a11y regression corpus | Planned |
| `VISUAL-061` | Tabs, containers, navigation groups, backdrops, and Identity remain readable across narrow, forced-colors, print, and reduced-transparency modes. | Browser screenshots/DOM assertions and static theme checks | Planned |
| `CONCURRENCY-061` | Concurrency, retry, timeout, cancellation, and idempotency policies are explicit and safe. | Duplicate/retry/cancel/replay corpus | Planned |
| `STALE-061` | Late, duplicate, cancelled, revision-incompatible, or unauthorized results cannot update current state. | Deterministic race and permission-change tests | Planned |
| `FORM-061` | Native, HTMX, and Required element forms agree on validation, busy, focus, duplicate submit, and retry. | Host/browser/keyboard matrix | Planned |
| `JOB-061` | Jobs and refreshable views project terminal, expired, disconnect, reconnect, and poll behavior consistently. | Backend/worker/reconnect fixtures | Planned |
| `HOST-061` | Every first-party host/package has an accepted Required/Progressive/Experimental/Deferred/Excluded disposition. | Inventory plus package-specific conformance | Planned |
| `TRACE-061` | One redacted portable trace schema represents lifecycle and target transitions across tools. | Golden JSON, pytest/browser/Explorer parity, malformed input | Planned |
| `SECURITY-061` | State and traces preserve CSRF/auth/tenant/replay/target/cache/redaction boundaries. | Adversarial control-plane matrix | Planned |
| `A11Y-061` | All lifecycle states have semantic, keyboard, focus, announcement, reduced-motion, and no-JS behavior. | Automated semantics plus browser evidence | Planned |
| `PERF-061` | Frozen envelope/trace/nesting/retry/poll/retention budgets pass at and beyond limits. | Reproducible benchmark and resource-limit report | Planned |
| `DOCS-061` | API, lifecycle diagrams, fallback, errors, diagnostics, migration, and recipes match runtime maturity. | Link/API example checks and docs build | Planned |
| `UPGRADE-061` | Existing handles/forms/jobs/fragments/elements retain behavior and have a documented rollback path. | Before/after fixtures and deprecation assertions | Planned |
| `PKG-061` | Clean wheels expose identical version/schema/maturity facts and the reference app uses packaged imports. | Build/install/package identity and production-like smoke | Planned |

## Release decision

Release requires every Required row Verified, zero Deferred Required capabilities, no competing
lifecycle vocabulary in Required adapters, passing fallback with all enhancements disabled, and a
signed-off compatibility/rollback packet. Progressive and Experimental rows retain their labels in
docs, Explorer, metadata, and package manifests.
