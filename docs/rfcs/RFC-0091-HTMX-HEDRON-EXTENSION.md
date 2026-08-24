# RFC-0091: Hedron HTMX interaction extension

**Status:** Proposed  
**Proposed phase:** 0.64  
**Depends on:** RFC-0009, RFC-0031, RFC-0070, RFC-0072, RFC-0075, RFC-0090

## Summary

This RFC proposes `htmx-ext-hedron`, a small first-party HTMX 2 extension that projects
Hedron's server-authored interaction contracts into browser lifecycle behavior.

The extension makes pending, success, error, cancellation, supersession, focus, accessibility,
and trace behavior consistent across Hedron forms, commands, refreshable views, jobs, fragments,
and supported Web Components. It consumes the lifecycle, operation identity, and trace contracts
defined by phases 0.61–0.63; it does not create a second state authority.

The extension is an explicitly declared, locally served, pinned asset. It is not a replacement for
HTMX, a virtual DOM, a client-side store, a hydration layer, or a requirement for Node.js.

## Problem statement

Hedron already has server-side contracts for action state, async boundaries, stale-result handling,
accessibility, and interaction tracing. HTMX currently provides the transport and swap mechanics,
but applications still need repeated browser-side glue for:

- pending and terminal state projection;
- disabled controls, `aria-busy`, live announcements, and focus movement;
- distinguishing stale, cancelled, superseded, and failed requests;
- initializing and cleaning up browser behavior around fragment swaps; and
- correlating browser events with Explorer and test traces.

That glue is easy to implement inconsistently and often leads to inline `hx-on:*` handlers or
application-specific JavaScript. A first-party extension can provide the browser projection while
leaving state, authorization, mutation, and HTML rendering on the server.

## Design principles

1. HTMX owns request dispatch and DOM swapping.
2. Hedron's server contracts own operation identity, authorization, validation, mutation, and
   terminal outcomes.
3. The extension may improve presentation but must never be a correctness or security dependency.
4. Native HTML and full-page/full-fragment responses remain the Required fallback.
5. All public browser facts are bounded, redacted, versioned, and inspectable.
6. Registered modules replace inline executable attributes under strict CSP; arbitrary response
   scripts remain disabled.
7. The asset is local, pinned, digest-checked, and loaded only when declared.

## Phase allocation

| Area | Phase 0.64 outcome |
|---|---|
| Extension identity | Add the closed public id `hedron` and pinned `htmx-ext-hedron` asset. |
| Lifecycle projection | Project the frozen 0.61 lifecycle into `data-hedron-state` and namespaced browser events. |
| Interaction UX | Coordinate busy, disabled, announcement, focus, reduced-motion, and error presentation. |
| Concurrency | Consume 0.61 operation generations and 0.62 navigation policy to suppress stale browser updates. |
| Fragment lifecycle | Provide CSP-safe registration and cleanup hooks for supported charts, maps, grids, and elements. |
| Observability | Emit the 0.61/0.63 portable trace facts to browser tests, Explorer, and diagnostics. |
| Hedron integration | Add declaration, asset planning, component markers, browser tests, simulator support, and docs. |

## Proposed browser contract

The final names are frozen during Stage 0. The intended surface is:

```html
<form
  hx-post="/profile"
  hx-target="#profile"
  data-hedron-state-host
  data-hedron-concurrency="latest"
  data-hedron-focus="error"
  data-hedron-announcement="polite"
>
  ...
</form>
```

The extension may project:

- `data-hedron-state="idle|pending|success|error|cancelled|stale|conflict"`;
- `data-hedron-operation`, `data-hedron-generation`, and bounded trace identifiers;
- `aria-busy`, disabled state, live-region announcements, and validation focus;
- namespaced lifecycle events such as `hedron:pending`, `hedron:success`,
  `hedron:error`, `hedron:cancelled`, `hedron:superseded`, and `hedron:settled`; and
- a CSP-safe registration API for explicitly registered modules to initialize after load and clean
  up before removal.

These are candidate names, not a frozen API. They become authoritative only after the 0.64 Stage 0
contract lock.

## Server boundary

The extension consumes existing HTMX response status, `HX-*` headers, Hedron interaction metadata,
and the frozen 0.61/0.63 trace envelope. It must not infer server authorization or mutation success
from client attributes. If a new response fact is required, it must be added to the typed Hedron
response contract first and exposed through a validated header or bounded fragment marker.

## Lifecycle registry

The extension may expose a small registry for trusted, application-owned modules:

```javascript
hedron.register("#chart", {
  afterSwap(element) {},
  beforeCleanup(element) {},
});
```

Registration is explicit, CSP-compatible, scoped to declared selectors, and teardown-aware. It is
not a general event-bus replacement, an inline-code escape hatch, or permission to execute scripts
from response HTML.

## Capability dispositions

| Capability | Disposition |
|---|---|
| Local pinned extension asset and explicit `Page` declaration | Required |
| Lifecycle state projection and trace correlation | Required |
| Busy/disabled/announcement/focus behavior | Required |
| Stale/superseded response presentation | Required |
| CSP-safe lifecycle registry and cleanup | Required for inventoried first-party consumers |
| Explorer/browser trace integration | Required |
| Native HTML and full-page fallback | Required |
| SSE/WebSocket transport | Consume existing dispositions; not promoted by this RFC |
| Idiomorph or a new morph engine | Excluded from 0.64 |
| Global client store, hydration, VDOM, JSX, React semantics | Excluded |
| Arbitrary response scripts or inline executable `hx-on:*` | Excluded by default |

## Compatibility and rollback

- Pages without `htmx_extensions={"hedron"}` receive no extension bytes and retain current behavior.
- Removing the declaration restores ordinary HTMX behavior.
- Existing `hx-*` attributes, `InteractionResult`, `ActionHandle`, `AsyncRegion`, and element
  contracts remain valid.
- The extension may only add presentation and diagnostics; it cannot change server authorization,
  target allowlists, cache policy, or mutation semantics.
- Unknown extension metadata fails closed in development and degrades to the ordinary HTMX path in
  production according to the existing extension policy.

## Non-goals

- Reimplementing HTMX request, swap, history, or selector semantics.
- Making browser state authoritative over server state.
- Adding a required build tool, npm dependency, or client application framework.
- Reopening `hx-sse`, `hx-ws`, Idiomorph, or arbitrary community-extension support.
- Providing optimistic mutation semantics; those remain governed by the 0.62 server contract.

## Acceptance

Phase 0.64 is releasable only when the extension passes the contract, asset, lifecycle, accessibility,
concurrency, CSP, browser, trace, simulator, package, documentation, and rollback gates in
[RELEASE_0_64](../acceptance/RELEASE_0_64.md).
