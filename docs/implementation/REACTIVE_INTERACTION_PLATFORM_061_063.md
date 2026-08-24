# Reactive interaction platform: 0.61–0.63 program plan

**Status:** Proposed / Stage 0 planning  
**Authority:** [RFC-0090](../rfcs/RFC-0090-REACTIVE-INTERACTION-PLATFORM.md)

## Outcome

Phases 0.61–0.63 turn Hedron's shipped interaction capabilities into one coherent, inspectable
platform. The program adopts React's strongest transferable ideas—shared lifecycle vocabulary,
boundaries, identity, transitions, bounded optimism, and tooling—without importing React's renderer
or making browser state authoritative.

## Phase plans

| Phase | Contract freeze | Delivery plan | Acceptance plan |
|---|---|---|---|
| 0.61 | Lifecycle, operation identity, async-region lowering, trace schema | [Action state and async boundaries](ACTION_STATE_ASYNC_061.md) | [Release 0.61](../acceptance/RELEASE_0_61.md) |
| 0.62 | Navigation, failure isolation, optimistic risk classes, identity transfer | [Navigation, optimism, and failure isolation](NAVIGATION_OPTIMISM_062.md) | [Release 0.62](../acceptance/RELEASE_0_62.md) |
| 0.63 | Theme contract completion, profiler, checks, metadata ABI, migration dispositions | [Theme contract, interaction tooling, and interoperability](INTERACTION_TOOLING_063.md) | [Release 0.63](../acceptance/RELEASE_0_63.md) |

The shared [acceptance rules](../acceptance/REACTIVE_INTERACTION_PHASES_061_063.md) define maturity
and evidence semantics for all three releases.

## Program dependency graph

```text
existing handles / forms / jobs / fragments / InteractionState / OptimisticMutation
                                  |
                                  v
0.61 lifecycle + operation identity + async lowering + portable trace schema
                   |                              |
                   v                              |
0.62 navigation + failure isolation + bounded optimism + identity diagnostics
                   |                              |
                   +------------------------------+
                                  v
0.63 theme resolution + conformance + profiler + static checks + metadata + migration dispositions
```

0.61 owns vocabulary and serialization. 0.62 consumes that vocabulary for browser behavior. 0.63
consumes both phases for tooling while completing the 0.60 theme contract at the stylesheet,
component-manifest, export, and evidence boundaries. Parallel implementation may prototype
downstream consumers, but no downstream phase may freeze a conflicting contract or create a second
theme/metadata authority.

## Cross-phase invariants

1. Server state is authoritative for identity, authorization, tenancy, validation, mutation, and
   durable persistence.
2. Ordinary HTML/HTTP or a full-fragment response is the Required fallback.
3. One operation has one identity, generation, target set, and terminal outcome.
4. One mutable field has one authoritative writer; transfer and shared reads are explicit.
5. Late, duplicate, cancelled, unauthorized, and revision-incompatible responses cannot overwrite
   current state.
6. Optimism is reversible, revisioned, idempotent, resource-bounded, and limited to approved risk
   classes.
7. Traces and diagnostics are versioned, deterministic, redacted, and bounded.
8. Browser enhancements are capability-detected and never security or correctness dependencies.
9. Supported installation and core authoring do not require npm, Node, JSX, React, or hydration.

## Program workstreams

| ID | Workstream | Owner phase | Completion condition |
|---|---|---|---|
| P0 | Predecessor reconciliation | 0.61 | Every existing authority is consumed, adapted, deprecated, or explicitly retained. |
| P1 | Contract and disposition locks | Each | Public schema, host/package matrix, maturity, diagnostics, and budgets are machine-readable. |
| P2 | Core and host implementation | 0.61–0.62 | FastAPI flagship and required host paths share semantics without copied business logic. |
| P3 | Elements and browser behavior | 0.61–0.62 | Native, HTMX, and element paths pass the same lifecycle, a11y, race, and fallback corpus. |
| P4 | Trace, theme, and tooling convergence | 0.61–0.63 | One trace and one resolved theme/metadata authority feed tests, Explorer, CLI, profiler, exports, and conformance. |
| P5 | Fleet adoption | Each | Reference app and inventoried first-party consumers adopt or record an explicit disposition. |
| P6 | Upgrade and packaging | Each | Before/after fixtures, package parity, rollback, release notes, and clean-wheel tests pass. |

## Package ownership

| Package/area | 0.61 | 0.62 | 0.63 |
|---|---|---|---|
| `hedron-core` | Lifecycle, identity, boundary/trace schemas | Navigation/failure/optimistic policy schemas | Theme resolution/export, diagnostic, manifest, and metadata schemas |
| `hedron` | FastAPI adapters and response lowering | Navigation/failure host integration | Theme CSS/bundles, CLI checks, inspection, and trace export |
| `hedron-elements` | Lifecycle and async projections | Browser navigation, failure, and optimistic projections | Typed parts/slots/state hooks and custom-element metadata |
| `hedron-data` | Existing mutation adapter | Approved optimistic data workflows | Data diagnostics and migration facts |
| `hedron-explorer` | Read-only lifecycle view | Race/identity/failure explanations | Profiler, theme inspector, state matrix, and source-linked reports |
| `hedron-charts` / visualization adapters | Existing chart contracts | — | Theme-aware palettes, non-color encodings, and accessible fallback facts |
| `hedron-conformance` | Portable lifecycle/trace fixtures | Browser/failure/optimism fixtures | Theme/trace/check/metadata/state-matrix conformance |
| Flask/Django adapters | Stage 0 disposition | Required or documented retained behavior | Conformance/report consumption |

The exact Required/Progressive/Experimental disposition is locked independently in each phase; this
table identifies ownership, not maturity.

## Reference-application vertical slices

Every phase extends the same journeys so evidence accumulates instead of creating isolated demos:

1. A form command with validation, pending, cancellation, retry, success, and no-JavaScript submit.
2. A lazy dashboard panel with empty, loading, timeout, stale, and localized-error presentations.
3. A revisioned DataEditor mutation with confirmation, rollback, conflict, and permission change.
4. Boosted navigation preserving URL, title, history, focus, scroll policy, and full-page fallback.
5. A coordinated dashboard with bounded fan-out, cancellation, cache variation, and one failed panel.
6. Explorer and CLI explanations generated without executing application callbacks.
7. A React migration example showing native mapping, manual redesign, and an honest unsupported case.
8. A custom-theme fixture that exercises built-in components, exported tokens, conformance, and the
   portable state matrix without application-authored CSS.

## Stage sequence

| Stage | Purpose | Exit condition |
|---|---|---|
| Stage 0 | Reconcile and lock | Decisions, schemas, budgets, diagnostics, dispositions, issue mirrors, and acceptance artifacts approved. |
| Stage 1 | Core vertical slice | One native/HTMX/reference journey proves the contract end to end. |
| Stage 2 | Fleet and host adoption | Required packages/hosts consume the same contract and old paths remain compatible. |
| Stage 3 | Adversarial closure | Security, a11y, races, limits, browsers, multi-worker, and upgrade evidence pass. |
| Stage 4 | Release | All Required gates Verified, docs/package artifacts agree, and rollback is documented. |

## Program stop conditions

Pause and return to Stage 0 if implementation requires a second state authority, trusts browser
status for server decisions, makes a progressive transport required, cannot bound retained data, or
requires React/Node for a Supported path. A downstream phase also stops if it needs to reinterpret a
frozen upstream state or trace field.

## Success measures

- One lifecycle/trace vocabulary covers all inventoried supported asynchronous interactions.
- Reference journeys contain no duplicated mutation or authorization logic across native, HTMX, and
  element paths.
- Stale/duplicate/cancelled response tests have zero state-corruption escapes.
- Every optimistic Supported row has a recorded risk class and rollback/conflict proof.
- Explorer, CLI, browser tests, and conformance agree on trace identifiers, outcomes, resolved theme
  values, and component contract identity.
- A supported custom theme reaches built-in component states through public contracts, with any
  Progressive visual extension explicitly labeled and safely degradable.
- Existing applications retain ordinary server behavior without adopting the new APIs.

Numeric latency, size, memory, retention, and fan-out budgets are intentionally not guessed in this
overview. Each Stage 0 plan must freeze reproducible values from baseline probes before coding.
