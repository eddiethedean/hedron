# Phase 0.61: unified action state and server-first async boundaries

**Status:** Implementation baseline complete / release evidence pending
**Predecessor:** published 0.60 baseline  
**Authority:** [RFC-0090](../rfcs/RFC-0090-REACTIVE-INTERACTION-PLATFORM.md)  
**Acceptance:** [RELEASE_0_61](../acceptance/RELEASE_0_61.md)

## Outcome

Forms, action handles, jobs, refreshable fragments, and supported Web Components expose one
versioned lifecycle and one server-first boundary model. Applications can render pending and failure
states consistently, reject stale work, and inspect transitions without adding application
JavaScript.

Phase 0.61 also closes the small-surface consistency packet tracked by issues #668–#672: Tabs,
bounded Container layout, standalone NavGroup, AmbientBackdrop, and default-theme Identity text
layout. These are additive presentation contracts and do not create a competing interaction store.

## Entry gate

Stage 1 cannot begin until Stage 0:

- inventories `InteractionState`, handles/results, forms, jobs, fragments, HTMX indicators,
  optimistic mutations, and element async states;
- resolves final public names and serialization version;
- locks transition, operation-identity, concurrency, retry, cancellation, timeout, and stale rules;
- records package/host maturity and compatibility dispositions;
- freezes redaction and numeric resource/performance budgets from reproducible probes; and
- creates issue mirrors for every Required workstream and gate.

## Candidate public contracts

Names are provisional until Stage 0. Behavior is the contract.

| Contract | Responsibility | Explicit limit |
|---|---|---|
| `ActionState` | Read-only projection of one operation's lifecycle and bounded public status. | Not a durable/global browser store. |
| `ActionPhase` | Closed lifecycle vocabulary: idle, pending, success, error, cancelled, stale, conflict. | Extensions require a schema-version decision. |
| `OperationIdentity` | Stable operation id, generation, target, correlation, and optional base revision. | Carries no authorization claim. |
| `ActionPolicy` | Concurrency, retry, timeout, stale-result, cancellation, and idempotency behavior. | Hidden retries are forbidden for unsafe/non-idempotent work. |
| `AsyncRegion` | Server-authored initial/pending/empty/success/error/timeout/cancelled/retry presentation. | Does not suspend arbitrary Python or require hydration. |
| `InteractionTrace` v1 | Redacted, ordered lifecycle/target/transport facts for tools and tests. | No unrestricted payload capture. |

`ActionState` adapts existing `InteractionState`; it does not replace element state ownership.
`AsyncRegion` lowers through existing render/fragment/job/action mechanisms and always has an
ordinary HTTP or full-fragment result.

### Surface consistency packet

| Issue | Implemented contract | No-JavaScript / compatibility rule |
|---|---|---|
| #668 | `Tabs(appearance=..., density=..., responsive=...)` with closed tokens and scroll-safe overflow. | Existing markup and keyboard enhancement remain the default when tokens are omitted. |
| #669 | `Container(max_width=..., align=..., padding=...)` with finite theme markers. | Existing query/name behavior and default layout remain unchanged. |
| #670 | Public `NavGroup`, reused by `AppShell(nav_groups=...)`. | Group markup is ordinary semantic HTML and can be returned in a fragment/OOB response. |
| #671 | `AmbientBackdrop` with finite pattern/tone/intensity tokens and an inert decoration layer. | Content stays in document order; print, forced-colors, and reduced-transparency hide decoration. |
| #672 | Default theme stacks and constrains Identity primary/detail text. | Long identity content remains readable without application CSS. |

The surface packet is verified by `tests/unit/test_phase061_action_state.py`, import-surface
checks, CSS parity checks, and the existing shell, a11y, and component composition suites.

## Required transition invariants

```text
idle -> pending -> success
               -> error -> pending (explicit retry, if allowed)
               -> cancelled
               -> stale
               -> conflict
```

- One operation has at most one terminal outcome.
- Retry creates a new attempt/generation; it does not rewrite prior trace history.
- Cancellation is best-effort for work execution but definitive for whether that generation may
  update its target.
- A stale or revision-incompatible response is observable but cannot update current presentation.
- Error messages exposed publicly are bounded and redacted; internal causes stay in server logs.
- Reconnect or duplicate delivery cannot duplicate a committed mutation.

## Workstreams

| ID | Workstream | Deliverables |
|---|---|---|
| W0 | Reconciliation and locks | Authority inventory, collision analysis, transition/schema lock, host/package disposition, budgets, diagnostics. |
| W1 | Core lifecycle | Immutable models, validation, serialization, transition reducer, operation generations, deterministic errors. |
| W2 | Policy and races | Concurrency modes, stale rejection, cancellation, explicit retry, timeout, idempotency/replay integration. |
| W3 | Async-region lowering | Semantic HTML states, full-page/full-fragment fallback, polling/HTMX progressive adapters, nested-boundary limits. |
| W4 | Forms and commands | Native/HTMX/element parity for busy, validation, focus, disabled controls, duplicate submit, retry. |
| W5 | Jobs and refreshable views | Job/poll/refresh adapters, disconnect/reconnect, terminal-state projection, expired-result behavior. |
| W6 | Elements | Property/event/state projection, lifecycle cleanup, transfer compatibility, no-JavaScript fallback. |
| W7 | Catalog and trace | Catalog fields, manifest/package projections, trace v1, JSON export, redaction/truncation markers. |
| W8 | Explorer and diagnostics | Read-only timeline, source-linked explanations, stable `HED-ACTION-*` / `HED-ASYNC-*` identifiers. |
| W9 | Reference app and fleet | Seven program journeys, consumer inventory, explicit adopt/retain/defer/exclude records. |
| W10 | Adversarial evidence | CSRF/auth/tenant, race, multi-worker, payload, a11y, browser, performance, cleanup, package tests. |
| W11 | Upgrade and release | Before/after fixtures, deprecation plan, rollback, docs, changelog, clean-wheel verification. |

## Host and transport disposition to lock

| Surface | Planned disposition |
|---|---|
| FastAPI native forms/actions/jobs/fragments | Required flagship path. |
| Plain HTML/full navigation or full fragment | Required correctness fallback. |
| HTMX indicators/swaps/polling | Progressive; same lifecycle and server outcome. |
| Supported Hedron elements | Required where the element already owns async interaction. |
| Flask/Django | Stage 0 must choose Required parity or explicit retained legacy behavior per adapter. |
| SSE/WebSocket delivery | Experimental; cannot alter lifecycle correctness. |
| Third-party custom elements | Metadata/conformance opt-in; no implied support. |

## Diagnostics contract

Stage 0 assigns stable codes within these families:

- `HED-ACTION-*`: invalid transition, duplicate terminal result, unsafe retry, missing idempotency,
  operation/target mismatch;
- `HED-ASYNC-*`: missing fallback, incompatible nesting, unbounded retry/poll, target ownership error;
- `HED-TRACE-*`: truncation, unknown schema version, redaction failure, invalid ordering.

Every diagnostic has severity, source/provenance when known, remediation, deterministic ordering,
and a documented suppression policy. Security violations are not suppressible.

## Budgets to freeze in Stage 0

Measurements must establish limits for envelope bytes, public message bytes, trace events and total
trace bytes, nested regions, retained completed operations, retry attempts, poll frequency, server
retention, browser memory, render overhead, and catalog/manifest growth. Tests cover exact boundary,
one-over-boundary, truncation/degradation, and cleanup behavior.

## Compatibility and rollback

- Existing handles, forms, jobs, fragments, and `InteractionState` remain valid.
- Adapters preserve current rendering unless a lifecycle/boundary is declared or safely inferred
  under a locked rule.
- Unknown trace fields are ignored only where forward-compatible; unknown state semantics fail
  explicitly.
- Removing the new declaration restores the pre-0.61 ordinary server path.
- No migration requires browser persistence or a JavaScript build.

## Execution order

1. **E0:** W0 locks and baseline probes.
2. **E1:** W1 lifecycle plus portable unit fixtures.
3. **E2:** W2 race/idempotency policy and adversarial tests.
4. **E3:** W3 boundary lowering with native HTML vertical slice.
5. **E4:** W4–W6 adapters and browser parity.
6. **E5:** W7–W8 trace/catalog/Explorer convergence.
7. **E6:** W9 fleet adoption and reference journeys.
8. **E7:** W10–W11 closure, packaging, rollback, and release gate.

## Exit gate

0.61 ships only when every Required `*-061` row is Verified, no supported adapter has a competing
lifecycle vocabulary, native/HTMX/element paths agree on outcomes, stale/cancelled responses cannot
mutate current state, budgets are reproducible, and clean-package/reference-app evidence passes.
