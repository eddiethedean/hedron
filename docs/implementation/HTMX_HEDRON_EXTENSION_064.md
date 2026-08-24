# Phase 0.64: Hedron HTMX interaction extension

**Status:** Proposed / Stage 0 planning  
**Predecessor:** phases 0.61–0.63 and published HTMX 2 extension contracts  
**Authority:** [RFC-0091](../rfcs/RFC-0091-HTMX-HEDRON-EXTENSION.md)  
**Acceptance:** [RELEASE_0_64](../acceptance/RELEASE_0_64.md)

## Outcome

Hedron ships an explicitly declared `htmx-ext-hedron` asset that turns Hedron's existing server
interaction contracts into a consistent browser projection. Forms, actions, refreshable views,
jobs, fragments, and supported elements share pending/terminal state, accessibility behavior,
stale-response handling, lifecycle cleanup, and trace correlation without requiring inline handlers,
hydration, a client store, Node.js, or a second runtime.

## Entry gate

Stage 1 cannot begin until Stage 0:

- confirms the 0.61 lifecycle, operation identity, and trace schemas are stable enough to consume;
- inventories all first-party HTMX hosts and browser-owned consumers;
- freezes the public extension id, asset name, version, digest, load order, and declaration syntax;
- resolves the exact `data-hedron-*` markers and namespaced event vocabulary;
- defines the response facts required for success, stale, cancellation, and supersession;
- records CSP, accessibility, reduced-motion, browser, performance, and memory budgets; and
- creates issue mirrors for every Required workstream and gate.

## Architecture

```text
Hedron server contracts
  ActionState / OperationIdentity / AsyncRegion / InteractionTrace
                         |
                         v
HTMX request + response + swap lifecycle
                         |
                         v
htmx-ext-hedron
  state projection · a11y · focus · concurrency presentation · trace hooks
                         |
                         v
DOM / registered first-party modules / Explorer and browser evidence
```

HTMX remains the request and swap authority. Hedron's Python contracts remain the server and
security authority. The extension is a browser-side projection layer only.

## Candidate contract

The following is provisional until Stage 0:

| Surface | Responsibility |
|---|---|
| `Page(htmx_extensions={"hedron"})` | Explicitly request the local extension asset. |
| `data-hedron-state-host` | Opt a region into lifecycle projection. |
| `data-hedron-concurrency` | Select a declared presentation policy such as latest, replace, queue, or drop. |
| `data-hedron-focus` | Select safe focus behavior for success, error, or validation. |
| `data-hedron-announcement` | Select bounded polite/assertive/no announcement behavior. |
| `data-hedron-state` | Expose the current public lifecycle state. |
| `hedron:*` events | Offer namespaced browser lifecycle facts to registered modules and tools. |
| lifecycle registry | Initialize and teardown trusted modules around HTMX load/swap/cleanup events. |

The extension must not require authors to replace ordinary `hx-*` attributes.

## Workstreams

| ID | Workstream | Deliverables |
|---|---|---|
| W0 | Reconciliation and locks | Authority inventory, contract collision review, schema/version lock, dispositions, budgets. |
| W1 | Asset and declaration | Local extension asset, digest/license record, extension catalog entry, page planning, CSP/load-order integration. |
| W2 | Lifecycle projection | State markers, operation/generation correlation, terminal state handling, bounded metadata. |
| W3 | Accessibility UX | Busy/disabled behavior, live announcements, validation/error focus, reduced motion, keyboard and no-JS fallback. |
| W4 | Concurrency presentation | Latest/replace/drop/queue behavior, stale/superseded outcomes, navigation and fragment removal handling. |
| W5 | Lifecycle registry | Explicit module registration, selector scoping, initialization, teardown, duplicate-registration and cleanup rules. |
| W6 | Trace and diagnostics | Browser trace events, Explorer projection, test hooks, redaction/truncation, deterministic diagnostics. |
| W7 | Hedron integration | `hedron-core` extension metadata, `hedron` page/route integration, first-party component markers, simulator support. |
| W8 | Vertical slices | Form command, refreshable fragment, lazy/polling job, boosted navigation, chart/map/grid cleanup. |
| W9 | Adversarial/browser evidence | CSP, response spoofing, stale races, focus, accessibility, Chromium/Firefox/WebKit, performance, memory. |
| W10 | Upgrade and release | Existing behavior fixtures, opt-out/rollback, docs, clean wheels, package parity, changelog. |

## Host disposition

| Surface | Planned disposition |
|---|---|
| FastAPI forms, commands, refreshable views, and fragments | Required flagship integration. |
| Native HTML and full-page/full-fragment fallback | Required correctness path. |
| HTMX polling and lazy loading | Progressive; must retain current fallback. |
| `hedron-elements` lifecycle consumers | Required for inventoried Supported elements. |
| Charts, maps, grids, and other rich hosts | Required cleanup contract where already Supported; otherwise explicit disposition. |
| Flask/Django | Stage 0 chooses Required parity or documented retained behavior per adapter. |
| SSE/WebSockets | Consume existing Experimental/Deferred labels; no promotion. |
| Third-party modules | Experimental opt-in through the lifecycle registry. |

## Execution order

1. **E0:** W0 reconciliation, contract locks, browser/asset baseline, and issue mirrors.
2. **E1:** W1 asset declaration and a minimal form-command vertical slice.
3. **E2:** W2 lifecycle projection and W3 accessibility behavior.
4. **E3:** W4 stale/concurrency presentation and navigation/fragment integration.
5. **E4:** W5 registry plus chart/map/grid/element teardown slices.
6. **E5:** W6 trace/Explorer/browser-test integration and W7 simulator/package parity.
7. **E6:** W8 fleet vertical slices and W9 adversarial/browser/performance closure.
8. **E7:** W10 upgrade, documentation, rollback, clean-package verification, and release gate.

## Stop conditions

Pause and return to Stage 0 if the implementation requires a client-side source of truth, parses
unbounded response payloads, changes server authorization or target ownership, executes arbitrary
response scripts, makes the extension required for correctness, or cannot prove cleanup after a
fragment swap.

## Exit gate

0.64 ships only when every Required `*-064` row is Verified, the extension is opt-in and locally
served, the native/full-fragment fallback passes with the asset absent, first-party lifecycle
consumers clean up deterministically, stale responses cannot alter current presentation, and
browser/Explorer/test traces agree on the same bounded lifecycle facts.
