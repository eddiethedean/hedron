# RFC-0090: Reactive interaction platform without a client runtime

**Status:** Proposed  
**Proposed phases:** 0.61–0.63  
**Depends on:** RFC-0060, RFC-0070, RFC-0071, RFC-0072, RFC-0073, RFC-0077, RFC-0082,
RFC-0083, RFC-0085, RFC-0089

## Summary

This RFC proposes three independently releasable phases that borrow React's most transferable
lessons: uniform action lifecycles, explicit async and failure boundaries, stable identity,
responsive navigation, bounded optimistic feedback, and first-class developer tooling.

Hedron will express those lessons through server-authored Python, semantic HTML, HTMX, optional Web
Components, and portable evidence. It will not add a virtual DOM, mandatory hydration, a global
browser store, a required Node build, or React semantics to `hedron-core`.

## Problem statement

Hedron already supports forms, command handles, jobs, fragments, optimistic data edits, navigation,
Web Component state, interaction catalogs, replay-safe actions, and Explorer providers. Their
individual contracts are sound, but applications still need to reconcile several vocabularies for
pending work, stale results, errors, identity, cancellation, and traces.

React's advantage here is coherence. The opportunity for Hedron is to make its existing
server-authoritative capabilities compose as one inspectable platform without adopting React's
client-runtime architecture.

## Phase allocation

| Phase | Theme | Required outcome |
|---|---|---|
| 0.61 | Action state, async boundaries, and composed surfaces | Every supported asynchronous interaction projects one typed lifecycle, operation identity, fallback, and trace model; the five 0.60 surface seams share additive finite contracts. |
| 0.62 | Navigation, optimism, and failure isolation | Supported pages remain understandable and recoverable during navigation, mutation, stale responses, conflicts, and partial failure. |
| 0.63 | Tooling and ecosystem interoperability | Developers can inspect, check, profile, test, migrate, and extend the platform without adopting React. |

Each phase has its own implementation plan and release gate. Phase 0.62 cannot redefine the 0.61
lifecycle, and phase 0.63 cannot create a second trace or metadata authority.

## Predecessor authority

The program extends, rather than replaces, these shipped contracts:

| Existing authority | Program use |
|---|---|
| `InteractionState`, state ownership, and stable element identity | Project into the unified lifecycle and diagnose unsafe transfer. |
| `ActionHandle`, `InteractionResult`, effects, and outcomes | Supply action identity, server outcomes, and response lowering. |
| `OptimisticMutation` and collection revisions | Remain the mutation/rollback authority; 0.62 adds policy and approved use cases. |
| Refreshable views, jobs, fragments, and polling | Implement server-first async regions and fallback paths. |
| Interaction catalog, manifests, and package projections | Carry lifecycle, boundary, navigation, and tooling metadata. |
| HTMX extension activation and preload policy | Supply progressive transport and preload mechanisms when explicitly enabled. |
| Explorer providers and conformance reports | Host read-only traces, profiling, explanations, and portable evidence. |
| Replay-safe actions and the security control plane | Remain authoritative for CSRF, authorization, tenancy, idempotency, and redaction. |

No phase may silently fork these authorities. If Stage 0 finds a required incompatibility, the
phase must record a superseding decision and upgrade path before implementation begins.

## Capability dispositions

`Required` capabilities define release correctness. `Progressive` capabilities may improve the
experience but must preserve the Required fallback. `Experimental` capabilities carry no Supported
claim. `Excluded` capabilities are deliberate non-goals.

| Capability | 0.61 | 0.62 | 0.63 |
|---|---|---|---|
| Unified action lifecycle and operation identity | Required | Consume | Consume |
| Server-first async region and ordinary HTTP fallback | Required | Consume | Inspect |
| Polling and HTMX enhancement | Progressive | Progressive | Inspect |
| SSE/WebSocket delivery | Experimental | Experimental | Inspect only |
| Navigation policy and stale-navigation rejection | — | Required | Check/profile |
| Safe prefetch and View Transitions | — | Progressive | Check/profile |
| Revisioned optimistic mutations for approved risk classes | — | Required | Check/profile |
| Localized failure boundary | — | Required | Check/profile |
| Portable interaction trace and deterministic diagnostics | Schema Required | Consume | Required tooling |
| TypeScript element metadata | — | — | Required for Supported elements |
| React migration dispositions | — | — | Required documentation/tool output |
| Isolated React-island recipe | — | — | Experimental only |
| VDOM, hydration, hooks, JSX, global client store | Excluded | Excluded | Excluded |

## Public behavior

### Unified lifecycle

Phase 0.61 defines a versioned envelope that can represent `idle`, `pending`, `success`, `error`,
`cancelled`, `stale`, and `conflict`. It is a projection over existing action/form/job/fragment
authorities, not a new durable store. The envelope carries bounded public status, operation and
target identity, revision/correlation facts where applicable, retryability, and redacted diagnostics.

The same phase includes a bounded surface consistency packet: Tabs appearance/overflow tokens,
finite Container width/alignment/spacing, standalone NavGroup, inert AmbientBackdrop presets, and
constrained Identity text layout. These contracts consume the 0.60 theme authority and remain
server-rendered, additive, and safe when omitted.

State transitions must be monotonic for one operation. A late response cannot overwrite a newer
operation, a cancelled operation cannot re-enter `success`, and browser-provided status is never
trusted as proof of server acceptance.

### Async and failure boundaries

An async region is a server-authored descriptor for initial, pending, success, empty, timeout,
cancelled, error, and retry presentation. It lowers to ordinary HTML/full-fragment responses first;
polling, HTMX, or elements may enhance that path. It does not suspend arbitrary Python rendering or
promise to resume a browser component tree.

A 0.62 failure boundary localizes a declared region's presentation failure while preserving
unaffected regions. It does not swallow authorization failures, corrupt commits, or convert an
unknown partial mutation into success.

### Navigation and optimistic feedback

Navigation policy defines URL, title, history, focus, scroll, pending retention, stale-response
rejection, cache variation, and full-navigation fallback. Safe prefetch is same-origin, safe-method,
allowlisted, resource-bounded, and disabled for private/auth-sensitive responses unless explicitly
declared safe.

Optimistic behavior is available only to inventoried, reversible mutation classes. Every supported
use carries a base revision, idempotency key, authoritative confirmation, rollback, conflict
presentation, retained-history limit, and server revalidation. Authorization, payments, secret
changes, irreversible destruction, and cross-tenant movement cannot be optimistic.

### Tooling and interoperability

Phase 0.63 defines one portable, versioned, redacted trace consumed by pytest, browser tests,
Explorer, CLI output, and conformance. Static checks are deterministic and source-linked. Supported
Web Components publish generated metadata for properties, events, state ownership, lifecycle,
fallback, and compatibility.

Migration tooling produces dispositions—native mapping, bounded adapter, manual redesign, or
unsupported—instead of claiming semantic React conversion. Any React island remains isolated,
single-root, explicitly inventoried, removable, CSP-reviewed, and unable to own an HTMX server
region.

## Identity and ownership invariants

- Component, region, collection-item, operation, and writer identities are explicit where state can
  survive an update.
- One mutable state field has one authoritative writer at a time.
- Browser state may retain presentation but cannot grant identity, authorization, tenancy, or
  durable persistence.
- A response applies only to its declared target, operation generation, and compatible revision.
- State transfer across replacement is opt-in, bounded, schema-compatible, and observable.

## Security, privacy, and resource bounds

All phases preserve CSRF protection, authorization, tenant isolation, signed/replay-safe actions,
target allowlists, safe redirects, cache scope, payload limits, and server-side revalidation.
Traces, diagnostics, profiler records, migration output, and generated metadata are redacted by
construction and must not expose secrets, credentials, full private payloads, or unrestricted URLs.

Stage 0 of each phase locks exact limits for trace events/bytes, nesting, retained operations,
prefetch concurrency/bytes, retry count, profiler retention, and static-analysis work. Defaults fail
closed or degrade to the ordinary HTML/HTTP path when limits are reached.

## Accessibility

Pending, stale, empty, error, conflict, cancelled, retrying, and optimistic states require semantic
markup and deterministic keyboard/focus behavior. Status announcements must avoid duplicate or
high-frequency speech. Navigation preserves meaningful focus and document metadata. Motion honors
reduced-motion preferences; failure recovery remains available without animation or JavaScript.

The phase gates require automated semantics/keyboard/browser evidence and keep human assistive-
technology claims separate until real sessions exist.

## Performance and observability

The platform adds no mandatory persistent client loop. Metadata and traces are bounded, lazy, and
omittable in production where policy allows. New behavior receives budgets for HTML/metadata size,
interaction latency overhead, retained browser memory, server trace retention, and fan-out.

Profiler timing is diagnostic rather than a distributed tracing replacement. It must expose clock
source, sampling, truncation, and missing-data status.

## Compatibility and migration

- Existing forms, handles, fragments, jobs, `InteractionState`, `OptimisticMutation`, and full-page
  navigation remain valid.
- New adapters must be opt-in or behavior-preserving; no existing application is forced to adopt a
  boundary or optimistic policy.
- Serialized contracts are versioned with unknown-field tolerance where safe and explicit rejection
  where semantics could be misread.
- Each phase ships before/after fixtures, deprecation diagnostics, package identity checks, and a
  rollback path that restores ordinary server rendering.
- No phase changes the supported no-Node installation path.

## Alternatives considered

| Alternative | Disposition |
|---|---|
| Adopt React as Hedron's primary renderer | Rejected: creates a second authority and mandatory client runtime. |
| Build a Hedron virtual DOM/hydration layer | Rejected: high complexity and conflicts with server/HTML authority. |
| Leave every subsystem with independent states | Rejected: preserves current composition and tooling gaps. |
| Require live transports for responsive behavior | Rejected: weakens fallback and operational portability. |
| Allow arbitrary optimistic mutations | Rejected: authorization, conflict, and rollback risks are not bounded. |
| Document patterns without machine-readable contracts | Rejected: insufficient for conformance, Explorer, or static checks. |

## Open Stage 0 decisions

The following must be resolved per phase before implementation:

1. Final public symbol names and whether `ActionState` is exported directly or through a less
   collision-prone lifecycle namespace.
2. Exact transition table, serialization version, redaction fields, and extension rules.
3. Required versus Progressive host/package matrix for FastAPI, Flask, Django, elements, data,
   Explorer, and conformance.
4. Numeric resource/performance budgets and browser matrix.
5. Diagnostic identifiers, severity, suppression policy, and compatibility lifetime.
6. Whether the React-island recipe has enough value to remain Experimental in 0.63; omission is an
   acceptable result.

## Acceptance criteria

The RFC may be accepted when:

- all predecessor authorities and conflicts are inventoried;
- phase-specific contracts, workstreams, entry/exit gates, budgets, and package dispositions are
  approved;
- Required, Progressive, Experimental, Deferred, and Excluded claims are machine-readable;
- security, accessibility, performance, compatibility, migration, and rollback evidence is named;
- the reference application proves native HTML, HTMX, and element paths without duplicate business
  logic; and
- no Supported path depends on React, Node, hydration, SSE, WebSockets, preload, or View Transitions.

Implementation plans: [program overview](../implementation/REACTIVE_INTERACTION_PLATFORM_061_063.md),
[0.61](../implementation/ACTION_STATE_ASYNC_061.md),
[0.62](../implementation/NAVIGATION_OPTIMISM_062.md), and
[0.63](../implementation/INTERACTION_TOOLING_063.md).

Acceptance plans: [program rules](../acceptance/REACTIVE_INTERACTION_PHASES_061_063.md),
[0.61](../acceptance/RELEASE_0_61.md), [0.62](../acceptance/RELEASE_0_62.md), and
[0.63](../acceptance/RELEASE_0_63.md).
