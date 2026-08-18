# Hedron `v0.50` Explorer architecture acceptance

**Status:** Published in-tree `v0.50.0`; tag/PyPI deferred. Does **not** close `SR-021`.<br>
**Planning baseline:** Published in-tree `v0.49.1`<br>
**Required predecessor/cut baseline:** Verified `v0.49.1`<br>
**Target:** Hedron `v0.50.0`<br>
**Decision/RFC:** D-085 / D-086 / [RFC-0077](../rfcs/RFC-0077-EXPLORER-ARCHITECTURE.md)<br>
**Tracking:** [#501](https://github.com/eddiethedean/hedron/issues/501)<br>
**Related:** [#496](https://github.com/eddiethedean/hedron/issues/496)–[#500](https://github.com/eddiethedean/hedron/issues/500),
[#502](https://github.com/eddiethedean/hedron/issues/502),
[#503](https://github.com/eddiethedean/hedron/issues/503)

D-086 named shipped 0.49.1 Explorer seams (`explorer_router`, `ExplorerPanelMeta`,
frozen `/hedron-explorer/` mount/modes, CLI `inspect`/`graph`/`check`,
`diagnostics_to_sarif`). This cut ships the Stage 1 architecture on those seams.

## Release contract

- Public 0.49.1 mount, modes, HTML/JSON paths, and `ExplorerPanelMeta` stay.
- `ExplorerProvider` is additive in `hedron-core`; HTTP stays in `hedron-explorer`.
- Silent table slices become pagination or truncation diagnostics.
- CLI/HTML/JSON share identities, severity, and redaction; SARIF reuses
  `diagnostics_to_sarif`.
- Laboratory executes only declared safe preview ops; no invented auth.
- Catalog presence never grants production authority.

## Exact gate matrix

| Gate | Verified means |
|---|---|
| `ARCH-050` | Module boundary contract tests; thin `router.py`; golden route map; no dropped 0.49.1 routes. |
| `PROVIDER-050` | Provider v1 isolation: timeout, crash, ordering, skew, max payload, redaction; `ExplorerPanelMeta` compatibility. |
| `CONSUME-050` | Catalog, TypeSchema v2, handle-graph, OpenAPI, HTMX extension panels match 0.45–0.49 fingerprints. |
| `QUERY-050` | Search/filter/pagination on components, routes, catalog; truncation diagnostics replace silent `[:200]`. |
| `DIFF-050` | Deterministic baseline diff for catalog/manifest/routes/schema fingerprints; no fourth fingerprint authority. |
| `LAB-050` | TypeSchema v2 laboratory: `/api/simulate`, `/api/click-preview`, `/api/element-simulate`; redacted scenario export; no auth invention. |
| `HEADLESS-050` | CLI + JSON + HTML diagnostic identity/severity/redaction parity; `diagnostics_to_sarif` reused. |
| `ECOSYSTEM-050` | Every first-party projection labeled; one third-party provider; Flask/Django read-only labels, not `explorer_router` mount. |
| `SECURITY-050` | Production opt-in threat model; simulate/mutation bounds; CSRF frozen unless this gate explicitly changes it. |
| `PRIVACY-050` | Export/redaction; `REV-026-003` stays accepted risk. |
| `A11Y-050` | Keyboard, focus, landmark, no-JS fallbacks, contrast/motion/reflow for Supported Explorer workflows; not `EXPLORER-019`. |
| `BROWSER-050` | Chromium, Firefox, and WebKit journeys including provider crash. |
| `PERF-050` | Small/medium/large fixtures; query/memory budgets. |
| `RESILIENCE-050` | Cancellation; repeated-navigation leak checks. |
| `DOCS-050` | Provider author guide, migration from 0.49 hooks, upgrade matrices. |
| `COMPAT-050` | 0.49 consumers; frozen paths; rollback. |
| `PKG-050` | Clean wheel, optional-dep isolation. |
| `REGRESS-050` | Full Supported suite; no hidden Deferred claim; `EXPLORER-10-001` remains explicitly Deferred. |

## Stage 0 entry

- [x] D-085 and RFC-0077 define architecture, provider, query, headless, and exclusion boundaries.
- [x] API, implementation, inventory, upgrade, gate, roadmap, decision, and traceability artifacts exist.
- [x] Stage 0 changes documentation/contracts only; no 0.50 runtime/version claim.
- [x] D-086 rebases the living/planning baseline to Published in-tree `v0.49.1` and names shipped seams including `explorer_router` and `ExplorerPanelMeta`.
- [x] Tracking issue [#501](https://github.com/eddiethedean/hedron/issues/501) is bound.
- [x] Companion authoring [#496](https://github.com/eddiethedean/hedron/issues/496)–[#500](https://github.com/eddiethedean/hedron/issues/500) /
  [#502](https://github.com/eddiethedean/hedron/issues/502) /
  [#503](https://github.com/eddiethedean/hedron/issues/503) are bound to this phase
  (not Explorer gates).
- [x] In-tree Verified 0.49 is enough predecessor evidence; do not wait on PyPI/Git `#380` assets.
- [x] Stage 1 implements services, provider runtime, pagination, laboratory, and headless parity
  (in-tree `v0.50.0`; [#501](https://github.com/eddiethedean/hedron/issues/501) remains open for tag/PyPI).

Locks: [explorer-architecture-050.toml](explorer-architecture-050.toml) ·
[explorer-provider-050.toml](explorer-provider-050.toml) ·
[explorer-query-050.toml](explorer-query-050.toml) ·
[explorer-diff-050.toml](explorer-diff-050.toml) ·
[explorer-lab-050.toml](explorer-lab-050.toml) ·
[explorer-headless-050.toml](explorer-headless-050.toml).

## Cut rule

Do not cut `v0.50.0` until every non-disposition gate in
[`release-gate-0.50.toml`](release-gate-0.50.toml) is Verified. Deferred
`EXPLORER-10-001` / `EXPLORER-019` cannot appear in the Supported inventory.
`REV-026-003` remains accepted risk unless a later decision promotes it.
Companion authoring [#496](https://github.com/eddiethedean/hedron/issues/496)–[#500](https://github.com/eddiethedean/hedron/issues/500) /
[#502](https://github.com/eddiethedean/hedron/issues/502) /
[#503](https://github.com/eddiethedean/hedron/issues/503) must be closed or
explicitly deferred before the cut.
