# Phase 0.62: responsive navigation, bounded optimism, and failure isolation

**Status:** Proposed / Stage 0 planning  
**Predecessor:** verified 0.61 lifecycle and trace contracts  
**Authority:** [RFC-0090](../rfcs/RFC-0090-REACTIVE-INTERACTION-PLATFORM.md)  
**Acceptance:** [RELEASE_0_62](../acceptance/RELEASE_0_62.md)

## Outcome

Server-rendered applications remain responsive and recoverable during navigation and mutation.
Hedron preserves document semantics, stable identity, authoritative revisions, and unaffected
regions while making pending work, rollback, conflict, and partial failure explicit.

## Entry gate

Stage 1 requires a Verified 0.61 transition/trace schema plus Stage 0 locks for navigation state,
prefetch safety, identity transfer, optimistic risk classes, failure propagation, browser support,
diagnostics, and measured resource/performance budgets.

## Candidate public contracts

| Contract | Responsibility | Explicit limit |
|---|---|---|
| `NavigationPolicy` | URL/title/history, focus, scroll, pending retention, cache, stale rejection, and fallback. | Does not create a client router authority. |
| `TransitionPolicy` | Capability-detected visual transition and reduced-motion behavior. | Progressive only; never correctness-critical. |
| `OptimisticPolicy` | Approved risk class, revision, idempotency, confirm, rollback, conflict, and retention. | Extends `OptimisticMutation`; does not authorize. |
| `FailureBoundary` | Local pending/error/retry presentation and propagation rules for a declared target. | Cannot hide an uncertain or unauthorized mutation. |
| `StateTransferPolicy` | Explicit, schema-compatible, bounded transfer across declared replacement. | No ambient DOM scraping or duplicate writers. |

## Optimistic risk inventory

| Mutation class | Planned disposition | Minimum proof |
|---|---|---|
| Reversible toggle/favorite with server revision | Candidate Required | Idempotency, confirmation, rollback, permission recheck. |
| Inline scalar edit / DataEditor patch | Candidate Required | Base revision, validation, conflict presentation, bounded patch. |
| Reordering within one versioned collection | Candidate Required | Stable item keys, revision, deterministic rollback. |
| Bounded bulk action | Progressive pending Stage 0 probes | Per-item outcomes, size cap, partial-failure policy. |
| Dashboard filter that does not mutate durable data | Candidate Required | Stable query identity and stale-response rejection. |
| Authorization, role, tenant, payment, secret, destructive, cross-tenant action | Excluded | Must wait for authoritative server response. |
| Offline queue / multi-device merge | Excluded from 0.62 | Requires a separate durable synchronization RFC. |

Stage 0 converts every candidate into Required, Progressive, Experimental, Deferred, or Excluded.
Uninventoried mutation classes default to non-optimistic.

## Workstreams

| ID | Workstream | Deliverables |
|---|---|---|
| W0 | Reconciliation and locks | Existing navigation/preload/optimism/state-transfer inventory, risk matrix, browser matrix, budgets, diagnostics. |
| W1 | Navigation state machine | Start/retain/commit/reject/cancel/fallback rules; URL/title/history/focus/scroll semantics. |
| W2 | Safe prefetch | Same-origin safe-method allowlist, cache/private policy, concurrency/byte limits, cancellation, observability. |
| W3 | Progressive transitions | View Transition adapter, feature detection, reduced-motion/no-animation path, interruption cleanup. |
| W4 | Optimistic policy | Revision/idempotency/confirmation/rollback/conflict contract extending existing `OptimisticMutation`. |
| W5 | Approved mutation adapters | Toggle, scalar edit, ordering, DataEditor, bounded bulk, and dashboard-filter dispositions. |
| W6 | Failure isolation | Fragment/chart/table/job/element boundaries, retry/reconnect/cancel, uncertain-outcome escalation. |
| W7 | Identity and transfer | Stable keys/targets/writers, schema-compatible transfer, duplicate-writer and state-loss diagnostics. |
| W8 | Coordinated dashboards | Bounded fan-out, operation cancellation, stale results, cache variation, authorization changes. |
| W9 | Explorer/trace/browser | Navigation/mutation/failure timelines, source explanations, Chromium/Firefox/WebKit evidence. |
| W10 | Fleet and reference app | Adopt or disposition every first-party consumer; extend shared vertical slices. |
| W11 | Adversarial closure | Security, a11y, race, multi-worker, cache, offline/reconnect, resource, performance, cleanup. |
| W12 | Upgrade and release | Compatibility fixtures, rollback, docs, package parity, clean-wheel release evidence. |

## Navigation invariants

- A committed navigation has one canonical URL, title, history action, and focus destination.
- A response applies only to the active navigation generation and declared target set.
- Full-page navigation remains available when scripts, HTMX, preload, or transitions are absent.
- Prefetch never executes unsafe methods, carries no authority, and obeys cache/tenant/private policy.
- Interrupted transitions release overlays, focus traps, timers, listeners, and retained snapshots.
- Back/forward behavior is tested as browser history behavior, not simulated by a second router.

## Failure-boundary invariants

- Failure in one declared region preserves unrelated regions and their authoritative state.
- Parent propagation is explicit for missing fallback, corrupt shared shell, or policy-defined fatal
  outcomes.
- Unknown mutation outcome is presented as uncertain/reconcile-required, never silently rolled back
  or declared successful.
- Retry preserves idempotency and uses a new 0.61 operation attempt.
- Authorization and tenancy failures bypass optimistic confirmation and trigger safe reconciliation.

## Diagnostics contract

Planned families are `HED-NAV-*`, `HED-PREFETCH-*`, `HED-OPTIMISTIC-*`, `HED-FAILURE-*`, and
`HED-IDENTITY-*`. Required findings include unstable/missing key, duplicate writer, target mismatch,
unsafe prefetch, unbounded retention, excluded optimistic risk, missing rollback, stale apply,
uncertain outcome, state-transfer mismatch, and leaked transition resources.

## Budgets to freeze in Stage 0

Probes lock prefetch concurrency/response bytes/cache lifetime, retained navigation snapshots,
optimistic operations/history/patch size, collection size, fan-out, transition duration, retry and
reconnect work, browser memory, server overhead, and cleanup latency. Private/auth-sensitive
prefetch defaults off unless the lock proves an explicit safe policy.

## Compatibility and rollback

- Existing full-page and HTMX navigation remain valid and are the rollback path.
- Existing `OptimisticMutation` payloads remain valid; new policy fields use a versioned adapter.
- Applications opt into navigation retention, transition, and new optimistic classes.
- Unsupported browsers receive ordinary navigation and semantic pending/error content.
- Removing a policy cannot strand client-owned durable state because no such authority is created.

## Execution order

1. **E0:** W0 locks and 0.61 compatibility check.
2. **E1:** W1 navigation state machine with native/full-navigation fallback.
3. **E2:** W2–W3 prefetch and transitions behind Progressive declarations.
4. **E3:** W4 core optimistic policy and adversarial revision/idempotency corpus.
5. **E4:** W5 approved adapters; excluded classes remain server-confirmed.
6. **E5:** W6–W8 failure, identity, and dashboard vertical slices.
7. **E6:** W9–W10 tooling, browser matrix, fleet adoption.
8. **E7:** W11–W12 closure, packaging, rollback, and release gate.

## Exit gate

0.62 ships only when all Required `*-062` rows are Verified, full navigation remains correct,
optimistic scope exactly matches the locked risk inventory, stale/duplicate/conflicting work cannot
corrupt state, failures remain localized where declared, browser/a11y/security budgets pass, and all
retained resources are deterministically cleaned up.
