# What’s next

Hedron `v1.0.0` is implemented, Verified, tagged, and published. See
[Current release and support](current-release.md) for the exact channel status.

There is no committed 1.1 calendar or commercial SLA. Future work must preserve the 1.0 stable
inventory and pass the same evidence-driven compatibility, security, accessibility, packaging,
and migration review used for the 1.0 cut.

## Completed for 1.0

- Canonical `@app.page`, `@app.view`, and `@app.action` authoring roles.
- Static 0.67 migration diagnostics and conservative source migration tooling.
- A frozen stable inventory with SemVer compatibility protection.
- One explicit HTMX/Alpine/Web Component authority boundary.
- Stable `hedron-core` and `hedron` platform; Beta satellites, including `hedron-posit`, remain
  outside that boundary; `hedron-workbench` was removed.
- Python 3.10–3.14, FastAPI, Flask, Django, HDJ, browser, security, and package evidence.
- Polling as the Supported production fallback for asynchronous status.

## Candidates after 1.0

These are directions, not release promises:

| Area | Current boundary | Evidence required before promotion |
|---|---|---|
| Live SSE/WebSocket/streaming | Experimental; use polling | Multi-worker, proxy, backpressure, reconnect, browser, and failure evidence |
| Human assistive-technology sessions | Protocol engineering only | Compensated sessions and reviewed remediation; no automatic WCAG claim |
| Plotly/Altair production promotion | Experimental adapters | Offline assets, security, accessibility, export, and browser matrices |
| Morph-aware state retention | Deferred | One-writer ownership, stale-state, cleanup, focus, and fallback evidence |
| MCP mutations | Experimental and opt-in | Principal/tenant authorization, audit, replay, and failure-isolation evidence |
| Notebook multi-user hosting | Outside Supported scope | Explicit auth, isolation, resource, persistence, and operations design |
| Wider Web Component ecosystem | Bounded first-party ABI | Lifecycle, SSR/HTMX fallback, accessibility, security, and versioning contract |

## Deliberately not planned as defaults

- A required Node.js toolchain for ordinary Hedron applications.
- A client-side application store or virtual DOM as a second source of truth.
- Automatic plugin discovery in production without explicit risk acceptance.
- Explorer enabled by default in production.
- In-memory jobs or cache presented as multi-worker durable infrastructure.
- Hedron acting as an identity provider, ORM, or application authorization engine.
- Unqualified WCAG, SLA, LTS, or “all APIs are stable” claims.

## How future changes are accepted

1. Start from a documented adopter problem and identify the existing fallback.
2. Classify the proposed surface as stable, beta, experimental, internal, or deferred.
3. Prove compatibility with the 1.0 stable inventory and provide migration guidance for any
   changed beta/experimental contract.
4. Add security, accessibility, browser, performance, package, and rollback evidence in
   proportion to the claim.
5. Update [What’s ready](whats-ready.md), [Compatibility](../COMPATIBILITY.md), and the
   [release notes](release-notes.md) only after the evidence passes.

The long historical phase ledger remains available in
[`docs/ROADMAP.md`](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md), but it is
not an adopter roadmap.
