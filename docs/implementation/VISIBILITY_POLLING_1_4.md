# Phase 1.4: visibility-aware polling

**Status:** Proposed and unscheduled; planning only
**Planning revision:** 2026-10-28
**Baseline:** Published `v1.2.0`; rebase against the accepted 1.3 release at scope freeze
**Authority:** [RFC-0100](../rfcs/RFC-0100-INTERACTION-EFFICIENCY-AND-FORM-CONTINUITY.md) / D-121 planning sequence
**Acceptance:** [RELEASE_1_4](../acceptance/RELEASE_1_4.md) · [machine packet](../acceptance/release-gate-1.4.toml)
**Reference research:** [PHP interaction approaches](https://github.com/eddiethedean/hedron/blob/main/research/php-interaction-approaches-2026-10-28.md)

## Outcome

Long-open dashboards keep requesting status for hidden tabs and offscreen cards. Fixed intervals also synchronize traffic and repeat failures at the same rate.

A dashboard job card observes a synthetic export while visible, pauses under the selected hidden/offscreen policy, backs off after a scripted transient failure, refreshes once on return, and stops permanently at terminal state. A manual refresh link and ordinary status page remain usable.

## Existing seams and dependencies

Extend `Poll` in `hedron/builtins/live.py`, `PollPolicy` in `hedron/jobs/flow.py`, existing HTMX triggers, `ActionPolicy`, operation identities, and terminal job detection. Inventory existing browser timer throttling separately from Hedron policy; browser throttling is not a deterministic contract.

Phase 1.3 supplies the managed browser evidence protocol. Phase numbers express preferred release order; isolated inventory, design, and prototypes may proceed using current AppScenario/Playwright tests. Release predecessor `v1.3.0` and required contract evidence remain unsatisfied until recorded; a prototype is not release evidence. W0 names actual maintainers and freezes an explicit host matrix, including FastAPI, Flask/Django, HDJ, Edron, mounted paths, and no-JavaScript dispositions where applicable. Unsupported projections must be visible rather than silently skipped.

## Required scope

- Add opt-in hidden-tab and viewport scheduling policies with explicit keep-alive behavior. Preserve existing interval defaults and terminal-job stopping.
- Coalesce missed ticks; permit at most one fresh observation on visibility return and never replay a backlog. Jitter initial/resumed scheduling and bound retry/backoff after observation failures.
- Keep one in-flight observation per declared target; retain generation checks and honor server throttling, including an admitted Retry-After policy. A slower observation must not block an unrelated save action.
- Own observer/timer cleanup through the existing lifecycle coordinator. HTMX remains the sole application request executor; a visibility observer may signal eligibility but cannot call fetch.
- Expose bounded redacted reasons for active, hidden, offscreen, backoff, stopped, and removed scheduling states. Do not log response bodies or business data.

## Work packages

### W0 — Freeze scheduling semantics

Inventory intervals, job-stop behavior, HTMX synchronization, timers, and asset demands. Freeze the eligibility/backoff state machine, flag combinations, numeric limits, trace schema, browser/host matrix, ownership, and opt-in API tier against a recorded baseline.

### W1 — Deliver eligibility and lifecycle

Implement hidden-tab/viewport gating and explicit keep-alive projection through existing HTMX/lifecycle paths. Cancel scheduling when targets disappear, initialize each observer once, and retain manual HTTP fallback.

### W2 — Add bounded recovery

Integrate jitter, bounded failure backoff, server throttle handling, generation-safe single refresh on return, and existing terminal-job rules. Distinguish transport retry from application mutation retry.

### W3 — Prove the dashboard slice

Use the 1.3 harness and controlled dependencies to count actual requests across visible/hidden/offscreen, failure, return, target removal, nested replacement, and terminal states. Package docs and rollback evidence.

## Feature gates

| Gate | Required evidence |
|---|---|
| `SCHEDULE-140` | Hidden-tab/viewport eligibility, explicit keep-alive, timer/observer initialization and cleanup, one in-flight observation per target, and a manual status fallback. |
| `RECOVERY-140` | Bounded jitter/backoff and admitted Retry-After handling; at most one refresh on return; no queued-tick burst, mutation replay, stale commit, or terminal-job restart. |

The [acceptance packet](../acceptance/RELEASE_1_4.md) also requires scope/contract freeze, lifecycle, security, accessibility, performance, compatibility, docs, packaging, and release evidence. Every machine row remains Planned. No `check_140.py` or feature implementation is claimed by this document.

## Failure and resource evidence

Cover: Hidden/visible changes while a request is in flight; removed/recreated IDs; nested/OOB swaps; browser suspension; delayed responses; server 429; expired authentication; failure during return refresh; terminal result before the page becomes hidden.

Record request counts and worker CPU for the same dashboard under foreground, background, and offscreen workloads; freeze timing tolerances and request/observer/timer budgets before implementation. A selected pause policy dispatches zero new automatic observations while ineligible, excluding an already-dispatched request. Return produces at most one immediate observation; removed targets leave zero owned timers/observers.

Every observation retains route dependencies, principal/tenant checks, CSRF where applicable, target authorization, and no-store behavior. Do not refresh logged-out private content through a retained eligibility record.

Exercise Chromium, Firefox, and WebKit for admitted behavior, strict CSP, repeated/nested/OOB replacement, missing assets, and the declared HTTP fallback. Preserve one request executor and one presentation owner under the [HTMX/Alpine boundary](../api/HTMX_ALPINE_BOUNDARY_1_0.md). Candidate public policies are additive Beta until evidence selects a narrower maturity; omitted-policy defaults and existing stable symbols remain compatible.

## Prerelease checkpoints

| Checkpoint | Exit |
|---|---|
| `1.4a0` | Accepted detailed contract; FREEZE-140; exact APIs, matrices, numeric budgets, and executable evidence plan |
| `1.4a1` | Required reference flow, failure/recovery, HTTP fallback, and feature gates demonstrated in Chromium |
| `1.4b1` | Complete declared host/browser corpus, security/a11y/resource hardening, and current-default compatibility |
| `1.4rc1` | Clean package installs, docs, immutable gate evidence, migration/rollback, and all non-release rows Verified |

## Non-goals and rollback

SSE/WebSocket promotion, a durable scheduler, shared polling batches, changed global polling defaults, automatic mutation retries, or a second network runtime.

Remove the opt-in scheduling declaration to restore current fixed-interval polling; keep terminal stopping and manual refresh. Verify disabling the feature disposes its browser resources.

The 1.8 durable-workflow lane consumes this observation scheduling contract without inheriting a live-transport promotion.

Scope changes need a recorded amendment and matching roadmap/acceptance updates. Stage 1 entry is blocked on the detailed freeze, not granted by this planning packet. A release claim requires an explicit accepted release disposition and all Required rows Verified; skipped browser tests are incomplete evidence.
