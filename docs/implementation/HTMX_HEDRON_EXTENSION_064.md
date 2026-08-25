# Phase 0.64: bounded presentation and Hedron HTMX lifecycle interoperability

**Status:** Implemented core slice / Stage 0 evidence in progress
**Predecessor:** phases 0.61–0.63 and published HTMX 2 extension contracts  
**Authority:** [RFC-0091](../rfcs/RFC-0091-HTMX-HEDRON-EXTENSION.md)  
**Acceptance:** [RELEASE_0_64](../acceptance/RELEASE_0_64.md)
**Execution:** [EXECUTION_0_64](EXECUTION_0_64.md)

**Issue inventory:** Stage 0 tracks all 22 phase-owned open `enhancement` issues in the
[phase 0.64 roadmap inventory](../ROADMAP.md#phase-064-open-enhancement-inventory), including
the 0.62 carry-forward items. Issue #86 remains owned by phase 0.21.

## Refined phase boundary

0.64 is a coordinated two-track phase:

1. **Presentation contracts:** complete the finite, theme-backed authoring surface for semantic
   palette states, typography, spacing/geometry, parts/states/slots, responsive and container
   conditions, RTL/writing modes, native controls, data/visualization chrome, motion, and safe
   application-defined components.
2. **HTMX browser projection:** deliver the opt-in `htmx-ext-hedron` asset and lifecycle registry
   described by RFC-0091, consuming the frozen server contracts from 0.61–0.63.

The presentation track is the authority for tokens, public metadata, fallback behavior, and
conformance. The browser track may project those facts but cannot become authoritative. Every issue
in the roadmap inventory receives a Stage 0 disposition; only Required dispositions block the cut,
but Progressive and Experimental dispositions remain visible and evidence-backed.

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

### Presentation workstreams

| ID | Workstream | Issue coverage | Deliverables |
|---|---|---|---|
| P0 | Dispositions and dependency locks | All 22 | Issue-to-gate matrix, Required/Progressive/Experimental/Excluded decisions, compatibility and rollback rules. |
| P1 | Theme ABI and evidence | #680, #681, #682, #686, #687 | Derived semantic states, standalone conformance, CSS/token export, inspection diagnostics, parts/state manifest. |
| P2 | Semantic scales and composition | #677, #678, #683, #690, #692, #697 | Identity and global hooks, typography and geometry scales, typed slots, named motion with reduced-motion behavior. |
| P3 | Responsive and inclusive controls | #679, #695, #696, #698 | Viewport/container conditions, direction/writing modes, native control appearance, forced-colors/high-contrast fallbacks. |
| P4 | Component verticals and visual evidence | #685, #688, #689, #693, #694 | Visualization/data chrome, glass surfaces, public part/state recipes, component bundles, deterministic state-matrix visual evidence. |
| P5 | Safe custom-component styling | #699 | Scoped style DSL, bounded values/tokens, cascade layers, metadata, digest-stable allowlisted bundles. |

### HTMX extension workstreams

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

1. **E0:** P0/W0 reconciliation, issue dispositions, authority inventory, contract locks, and
   browser/asset baseline.
2. **E1:** P1 theme ABI/manifest locks plus W1 asset declaration and a minimal form-command slice.
3. **E2:** P2 semantic scales/composition plus W2 lifecycle projection and W3 accessibility
   behavior.
4. **E3:** P3 responsive/inclusive controls plus W4 stale/concurrency presentation and
   navigation/fragment integration.
5. **E4:** P4 component verticals and visual evidence plus W5 registry and chart/map/grid/element
   teardown slices.
6. **E5:** P5 safe custom-component styling plus W6 trace/Explorer/browser-test integration and W7
   simulator/package parity.
7. **E6:** W8 fleet vertical slices and W9 adversarial/browser/performance closure across both
   tracks.
8. **E7:** W10 upgrade, documentation, rollback, clean-package verification, disposition closure,
   and release gate.

## Stop conditions

Pause and return to Stage 0 if the implementation requires a client-side source of truth, parses
unbounded response payloads, changes server authorization or target ownership, executes arbitrary
response scripts, makes the extension required for correctness, or cannot prove cleanup after a
fragment swap.

## Exit gate

0.64 ships only when every inventory issue has an explicit disposition, every Required `*-064` row
is Verified, the extension is opt-in and locally served, the native/full-fragment fallback passes
with the asset absent, presentation contracts export deterministic metadata, first-party lifecycle
consumers clean up deterministically, stale responses cannot alter current presentation, and
browser/Explorer/test traces agree on the same bounded lifecycle facts.
