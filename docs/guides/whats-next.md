# What’s next

Hedron `v1.0.0` is implemented, Verified, tagged, and published. See
[Current release and support](current-release.md) for the exact channel status.

There is no committed 1.1 calendar or commercial SLA. The maintainer roadmap contains a proposed
1.X sequence, but these are planning candidates rather than release promises. Future work must
preserve the 1.0 stable inventory and pass the same evidence-driven compatibility, security,
accessibility, packaging, and migration review used for the 1.0 cut.

## Shipped in 1.0

- Canonical `@app.page`, `@app.view`, and `@app.action` authoring roles.
- Static 0.67 migration diagnostics and conservative source migration tooling.
- A frozen stable inventory with SemVer compatibility protection.
- One explicit HTMX/Alpine/Web Component authority boundary.
- Stable `hedron-core`, `hedron`, `edron`, `hedron-data`, `hedron-charts`, and `hedron-maps`
  platform; Beta satellites, including `hedron-posit`, remain outside that boundary;
  `hedron-workbench` was removed.
- Python 3.10–3.14, FastAPI, Flask, Django, HDJ, browser, security, and package evidence.
- Polling as the Supported production fallback for asynchronous status.

## Proposed 1.X sequence

These are planning candidates, not release promises. The sequence is ordered from adoption
confidence to higher-risk runtime and ecosystem expansion; each phase can end in promotion,
continued experimentation, or non-admission:

| Phase | Theme | Primary question |
|---|---|---|
| **1.1** | First-class UI testing and adoption confidence | Can a team test real UI behavior and diagnose failures with ordinary pytest? |
| **1.2** | Production async and durable workflows | Is anything beyond polling ready for production? |
| **1.3** | Inclusive and international UX | Can the stable surface work for more users and locales? |
| **1.4** | Visualization and media graduation | Which optional adapters meet the first-party contract? |
| **1.5** | Stateful browser composition | Can partial updates retain local state safely? |
| **1.6** | Controlled ecosystem expansion | Which advanced integrations have a trustworthy operating model? |

See the [full 1.X planning sequence](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md#proposed-1x-sequence)
for scope and shared entry/exit policy.

### Proposed 1.1 focus

The refined 1.1 candidate preserves fast render tests and `AppScenario`, then adds an optional
real-browser layer that manages the local application host, composes with Playwright, understands
Hedron interaction settling, correlates server/browser failures, and retains bounded redacted
failure evidence. Optional packages receive explicit testing-ownership dispositions and may add
package-native fixtures or semantics without another runner, browser harness, or ambient pytest
plugin. Pytest remains the runner, and no browser dependency enters ordinary Hedron applications.
Exact APIs and maturity remain blocked on the Stage 0 freeze; see
[RFC-0097](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0097-FIRST-CLASS-UI-TESTING.md)
and the
[acceptance plan](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_1_1.md).

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
