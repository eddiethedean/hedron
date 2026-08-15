# Phase 0.41 plan: browser composition, draft transfer, and navigation

**Status:** Implemented for the untagged `v0.42.0` release candidate; all D-069 gates Verified.

This plan turns [RFC-0060](../rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md) and D-069 into reviewable
work. Baseline: Published `v0.40.0`. Target: coordinated `v0.42.0`. Tracking:
[#96](https://github.com/eddiethedean/hedron/issues/96). Completion requires every row in
[`release-gate-0.41.toml`](../acceptance/release-gate-0.41.toml) Verified with zero Deferred.

## Architecture

| Layer | Owned contract | Failure boundary |
|---|---|---|
| Composition registry | Versioned event/detail schemas and allowlisted graph edges | Reject edge/graph; preserve native fallback |
| Graph runner | Correlation, visited-edge/depth bounds, cancellation/concurrency, authz recheck | Cancel one graph, never unrelated regions |
| Draft transfer | Declared draft fields; session-scoped, subject-bound envelope | Discard/reject entry; preserve server markup |
| Navigation bridge | Ordinary link/form baseline, HTMX history integration, fragment-only native motion | Full navigation or native fragment behavior |
| Restoration | Deterministic title, focus, scroll, validation and popstate rules | Main/native fallback without focus theft |
| Diagnostics | Content-free lifecycle/edge/state/outcome records | Drop trace; never block interaction |

## Contract artifacts

- Portable schemas for graph registrations, event details, transfer envelopes, and trace records.
- Positive/negative fixtures usable by Python, Node, and Java conformance evaluators.
- Reference flows: coordinated dashboard filters; form draft across an outer swap; submit/discard;
  boosted page navigation; fragment-only navigation; back/forward; failed/incompatible element.
- No-JS and storage-disabled fixtures are first-class expected paths, not exception tests.

## Work breakdown

### Stage 0 — contract and evidence packet (complete)

- Accept D-069 and RFC-0060 resolved questions.
- Lock release packet, planned gate manifest, upgrade matrix, and security-review brief.
- Bind #96 and the exact 14 regression issues; preserve Published `v0.40.0` living tip.

### Stage 1 — composition contracts (`COMPOSE-041`, complete)

- Define registry/fixture schemas and graph validation.
- Prove cycle/depth, target, payload, authz, cancellation/concurrency, late-response, and native
  fallback behavior.

### Stage 2 — bounded draft transfer (`STATE-041`, complete)

- Define envelope namespace, subject fingerprint, TTL/size/aggregate/single-consume policy.
- Prove submit/discard/logout/authority-change/incompatibility/rollback clearing and forbidden data.
- Preserve operation/revision identity and explicit conflict/rebase behavior.

### Stage 3 — navigation and restoration (`NAV-041`, complete)

- Integrate boosted snapshots without replacing HTMX history ownership.
- Prove native fragment-only behavior, title/focus/scroll restoration, preload/View Transition feature
  detection, reduced motion, and full-navigation fallback.

### Stage 4 — diagnostics and isolation (`TRACE-041`, `FALLBACK-041`, complete)

- Enforce a content-free trace schema and negative privacy fixtures.
- Inject slow module, exception, timeout, incompatible ABI, canceled request, corrupt storage, quota,
  and trace-sink failures; unrelated navigation/forms/regions must continue.

### Stage 5 — closure (`BROWSER-041`, `REGRESS-041`, `PKG-041`, complete)

- Run three engines, FastAPI/Flask/Django/HDJ/plugin/Workbench hosts, no-JS, a11y, privacy,
  performance/memory/leak, CSP/Trusted Types, mixed-version, upgrade, and rollback matrices.
- Close the exact 14-issue packet and publish only with zero Deferred 0.41 rows.

## Explicit non-work

Phase 0.42 alone owns whole-platform production-grade graduation. This implementation does not tag
or publish the 0.41 release candidate.
