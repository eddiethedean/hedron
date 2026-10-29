# Hedron `v1.4.0` visibility-aware polling acceptance plan

**Status:** Proposed and unscheduled; every gate Planned
**Authority:** [RFC-0100](../rfcs/RFC-0100-INTERACTION-EFFICIENCY-AND-FORM-CONTINUITY.md) / D-121 proposed planning sequence
**Implementation:** [VISIBILITY_POLLING_1_4](../implementation/VISIBILITY_POLLING_1_4.md)
**Machine packet:** [release-gate-1.4.toml](release-gate-1.4.toml)
**Required release predecessor:** `v1.3.0` (not yet satisfied)

This planning packet does not claim an implementation, checker, runtime behavior, final public API, or calendar commitment. Stage 1 requires FREEZE-140. Exact commands and immutable evidence paths must be selected at that freeze; planned CI-job labels below do not configure or imply existing feature jobs. Preserve phase 1.3's testing scope and the stable application inventory.

## Required reference flow

A dashboard job card observes a synthetic export while visible, pauses under the selected hidden/offscreen policy, backs off after a scripted transient failure, refreshes once on return, and stops permanently at terminal state. A manual refresh link and ordinary status page remain usable.

## Required gates

| Gate | Owner role | Required evidence |
|---|---|---|
| `FREEZE-140` | architecture | Accepted detailed RFC/phase contract; current-source inventory, named maintainers, exact additive APIs and diagnostics, required/deferred scope, host/maturity matrix, schemas, numeric limits, measured baselines, and exact executable commands/artifact paths. |
| `CONTRACT-140` | architecture | Existing HTMX/Alpine/element authorities and canonical handles reused; one transport/presentation owner; no duplicate state runtime; compatible omitted-policy defaults and documented invalid combinations. |
| `SCHEDULE-140` | browser-platform | Hidden-tab/viewport eligibility, explicit keep-alive, timer/observer initialization and cleanup, one in-flight observation per target, and a manual status fallback. |
| `RECOVERY-140` | runtime | Bounded jitter/backoff and admitted Retry-After handling; at most one refresh on return; no queued-tick burst, mutation replay, stale commit, or terminal-job restart. |
| `LIFECYCLE-140` | browser-platform | Repeated/nested/OOB replacement, removed targets, stale generations, asset failure, interruption, and teardown; exactly-once initialization/cleanup and zero retained owned resources after removal. |
| `A11Y-140` | accessibility | Keyboard/native fallback, focus and announcement ownership, semantic busy/error states, reduced motion, zoom/reflow, and the declared no-JavaScript flow; no blanket accessibility-conformance claim. |
| `SECURITY-140` | security | Every observation retains route dependencies, principal/tenant checks, CSRF where applicable, target authorization, and no-store behavior. Do not refresh logged-out private content through a retained eligibility record. |
| `PERF-140` | performance | Record request counts and worker CPU for the same dashboard under foreground, background, and offscreen workloads; freeze timing tolerances and request/observer/timer budgets before implementation. A selected pause policy dispatches zero new automatic observations while ineligible, excluding an already-dispatched request. Return produces at most one immediate observation; removed targets leave zero owned timers/observers. |
| `COMPAT-140` | compatibility | Stable inventory and current-default behavior preserved; explicit FastAPI/Flask/Django/HDJ/Edron/mount dispositions, strict CSP, three-browser evidence, unsupported combinations and Beta migration guidance. |
| `DOCS-140` | docs | Packaged reference flow and examples, policy defaults/limits, failure/recovery, HTTP fallback, privacy, diagnostics, API maturity, and exercised opt-out/rollback instructions. |
| `PKG-140` | packaging | Clean wheel/sdist base/extra installs, optional-import isolation, compatible pins and asset plans, typing, provenance/notices, and package/version evidence for every changed distribution. |
| `RELEASE-140` | release | Every other Required row Verified; immutable artifact-bound evidence, predecessor/support/maturity decisions, migration/rollback, and explicit release approval; no skipped Required row. |

## Adversarial and failure corpus

Hidden/visible changes while a request is in flight; removed/recreated IDs; nested/OOB swaps; browser suspension; delayed responses; server 429; expired authentication; failure during return refresh; terminal result before the page becomes hidden.

Use controlled dependencies and actual browser request/lifecycle facts through the existing AppScenario/Playwright facilities and the admitted 1.3 harness. Initial development can use current facilities, but release evidence must meet the frozen protocol and complete host/browser matrix. A screenshot or synthetic pure state test alone cannot satisfy browser behavior.

## Maturity, stop conditions, and rollback

Candidate policy APIs begin as additive Beta. Do not silently change defaults, promote SSE/WebSockets/morphing, bypass route dependencies, introduce response-supplied executable assets, or move application persistence/authorization into browser state. An unsupported host or browser row needs an explicit scope/maturity decision; skipping it cannot verify a Required gate.

Stop implementation or narrow the candidate if authority, native values, stale-result handling, required fallbacks, secret redaction, or resource cleanup cannot be preserved. Numeric limits and performance thresholds must be frozen from recorded baselines before implementation; passing a newly invented post-hoc budget is not acceptance.

Remove the opt-in scheduling declaration to restore current fixed-interval polling; keep terminal stopping and manual refresh. Verify disabling the feature disposes its browser resources.

The planning machine packet is intentionally not registered as a releasable phase in executable release tooling. Implementation must add the real checker, artifact/evidence binding, and tooling selection as reviewed work before any cut. Release requires all other Required gates Verified plus an explicit release decision; a planning edit cannot satisfy these conditions.
