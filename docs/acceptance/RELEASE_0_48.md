# Hedron `v0.48` HTMX extension integration acceptance

**Status:** Planned; Stage 0 contract refined by D-083 against Published in-tree `v0.47.0`<br>
**Planning baseline:** Published in-tree `v0.47.0`<br>
**Required predecessor/cut baseline:** Verified `v0.47.0`<br>
**Target:** Hedron `v0.48.0`<br>
**Decision/RFC:** D-080, refined by D-083 / [RFC-0075](../rfcs/RFC-0075-HTMX-EXTENSION-INTEGRATION.md)<br>
**Tracking:** [#373](https://github.com/eddiethedean/hedron/issues/373) owns every 0.48 gate. Do not start Stage 1 until this issue is bound and 0.47 is Verified in-tree.

## Release contract

- Extension declaration, activation, asset delivery, CSP, evidence, and diagnostics are one
  deterministic contract.
- Unused pages load no HTMX extension assets.
- SSE, head-support, and preload have complete packaged vertical slices with progressive fallback.
- Idiomorph ships only if its dedicated lifecycle gate passes; otherwise it remains explicitly
  excluded without weakening the other gates.
- Existing server-authoritative targeting, OOB, loading, security, and polling contracts remain in
  force.

## Exact gate matrix

| Gate | Verified means |
|---|---|
| `EXTENSION-048` | Closed catalog, declaration API, scope composition, typed components, HDJ evidence, deterministic manifests, and unknown/conflict failures pass. |
| `ASSET-048` | Demand-driven local pinned assets, digests/licenses, HTMX compatibility, dependency/load order, mount prefixes, CSP facts, deduplication, and zero unused-page assets pass. |
| `SSE-048` | Typed live/job regions, named swaps/triggers, reconnect/Last-Event-ID, terminal close, auth/tenant/limits, cleanup, observability, and polling fallback pass. |
| `HEAD-048` | Registered head assets, full-document/boosted merge, retain/add/remove/dedupe, title/metadata, CSP, failure, and rollback pass. |
| `PRELOAD-048` | Explicit cacheable GET preload, `HX-Preloaded` policy, pointer/keyboard/touch behavior, cache/auth partitioning, no mutation, and bounded amplification pass. |
| `MORPH-048` | Form/focus/custom-element/chart/OOB/a11y/three-engine lifecycle evidence admits morph, or a documented Deferred/excluded disposition prevents shipping it. |
| `SECURITY-048` | URL/origin/selector/event/head/eval boundaries, asset integrity, CSP, stream authz, cache isolation, rate/size/lifetime limits, HDJ evidence, and adversarial review pass. |
| `A11Y-048` | Semantic fallbacks, focus/live-region behavior, pause/control, reduced motion, keyboard/touch parity, head metadata, and scoped AT honesty pass. |
| `BROWSER-048` | Chromium/Firefox/WebKit activation, no-JS/CSP/failure, reconnect/navigation/swap/race/cancel/cleanup and memory-lifecycle evidence pass. |
| `PERF-048` | Asset/no-op bytes, parse/execute, SSE connection/reconnect, preload hit/waste/amplification, head/morph duration, and repeated-lifecycle budgets pass. |
| `ADAPTER-048` | FastAPI/Flask/Django/Posit/Workbench static paths, mounts, CSP, caching, streaming capability labels, and absence behavior pass. |
| `TOOLING-048` | Explorer, CLI, manifest, scenario, conformance, simulation, diagnostics, and static HDJ inspection agree without executing untrusted code. |
| `COMPAT-048` | Existing HTMX/OOB/InteractionResult/polling/pages, direct attributes, extension opt-out, upgrade, skew, deprecation, and rollback pass. |
| `DOCS-048` | Authoring, SSE/head/preload recipes, security, a11y, performance, operations, migration, troubleshooting, limitations, and extension-admission policy are complete. |
| `REGRESS-048` | Full Supported suite passes with no phase-owned blocker/high issue and no hidden Deferred claim. |
| `PKG-048` | Clean wheel/sdist, local assets/licenses/SBOM/provenance, Python/browser matrices, package data, versioning, and release rehearsal pass. |

## Stage 0 entry

- [x] D-080 and RFC-0075 define extension, asset, lifecycle, fallback, and authority boundaries.
- [x] D-083 rebases planning onto Published in-tree `v0.47.0` consume-shipped seams.
- [x] Roadmap, traceability, release acceptance, lock TOMLs, capability inventory, upgrade fixtures, implementation requirements, and planned public contract exist.
- [x] Stage 0 changes documentation/contracts only; no 0.48 runtime or version claim.
- [x] Verified 0.47 and a tracking issue are bound before Stage 1
  ([#373](https://github.com/eddiethedean/hedron/issues/373)).
- [ ] Stage 1 measures and locks asset, connection, amplification, lifecycle, and performance limits.

Contract locks: [catalog](htmx-extension-catalog-048.toml) ·
[assets](htmx-asset-activation-048.toml) ·
[SSE/head/preload](htmx-sse-head-preload-048.toml) ·
[morph/compat](htmx-morph-compat-048.toml) ·
[inventory](htmx-capability-inventory-048.toml) ·
[upgrade fixtures](upgrade-fixtures-048.md) ·
[implementation](../implementation/HTMX_EXTENSION_INTEGRATION_048.md) ·
[public contract](../api/HTMX_EXTENSIONS.md).

## Cut rule

Do not cut `v0.48.0` until every non-disposition row in
[`release-gate-0.48.toml`](release-gate-0.48.toml) is Verified with retained evidence. `MORPH-048`
must be either Verified or explicitly Deferred/excluded; a Deferred morph disposition cannot be
represented as a Supported capability.

