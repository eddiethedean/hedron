# RFC-0077: Explorer architecture and operator-grade development tooling

**Status:** Accepted<br>
**Target phase:** 0.50 (`v0.50.0`)<br>
**Decision:** D-085<br>
**Stage 0 contract refine:** D-086<br>
**Planning baseline:** Published in-tree `v0.49.1` (D-086)<br>
**Required predecessor/cut baseline:** Verified in-tree `v0.49.1`<br>
**Tracking:** [#501](https://github.com/eddiethedean/hedron/issues/501)<br>
**Related:** [#496](https://github.com/eddiethedean/hedron/issues/496)–[#500](https://github.com/eddiethedean/hedron/issues/500) /
[#502](https://github.com/eddiethedean/hedron/issues/502) /
[#503](https://github.com/eddiethedean/hedron/issues/503) —
companion 0.50 authoring; not Explorer gates<br>
**Extends:** RFC-0007, RFC-0014, RFC-0017, RFC-0024, RFC-0052, RFC-0057,
RFC-0072, and RFC-0076

**Revision:** 2026-08-18 — D-086 contract refine against Published in-tree `v0.49.1`:
planning baseline locked; architecture, provider, query, diff, lab, and headless
locks recorded; real `explorer_router`, `ExplorerPanelMeta`, frozen `/hedron-explorer/`
mount/modes, CLI `inspect`/`graph`/`check`, and `diagnostics_to_sarif` seams named.

**Post-cut:** Stage 1 shipped in-tree `v0.50.0`. Living tip is `v0.50.0`.
[#501](https://github.com/eddiethedean/hedron/issues/501) stays open for tag/PyPI.
Do not rewrite the Stage 0 contract above.
No runtime or version claim.

## Summary

Phase 0.50 turns `hedron-explorer` from a single FastAPI router module into a modular
development product whose browser UI and headless outputs share one query/model layer,
stay useful on large applications, and fail safely per panel. It does not change mount
modes, production refusal, or runtime authority.

**Operator-grade** means CI-friendly headless inspection artifacts and large-app
resilience, not production operations tooling. Explorer remains opt-in
(`explorer="off"|"development"|"secured"`) and is not a production default.

## Goals

- Decompose `hedron_explorer.router.explorer_router` (~1,366 lines today) into portable
  services plus a thin HTTP transport, with a golden route map so public 0.49.1 paths
  stay frozen.
- Introduce a versioned `ExplorerProvider` protocol in `hedron-core` with declared
  capabilities, timeout, ordering, redaction profile, and payload ceilings, without
  removing `ExplorerPanelMeta` or `register_explorer_panel`.
- Replace silent table slices (`[:200]`, a11y `[:40]`, audit `[:20]`,
  `CacheTrace.recent(50)`) with search/filter and cursor pagination or typed truncation
  diagnostics.
- Align CLI `hedron inspect` / `graph` / `check` / `routes` with Explorer HTML/JSON
  through shared services when `hedron-explorer` is installed; reuse
  `diagnostics_to_sarif` rather than a second SARIF writer.
- Add a bounded interaction laboratory over today's `/api/simulate`,
  `/api/click-preview`, and `/api/element-simulate` allowlists, plus a read-only package
  health slice that is not `hedron package doctor` (0.53).
- Keep Flask/Django Explorer consumption labeled and read-only; do not mount
  `explorer_router` on WSGI hosts.

## Non-goals and exclusions

- Reclassifying `EXPLORER-10-001` into a live SSE/WebSocket trace contract.
- Turning Explorer into a production default, unauthenticated endpoint, or authority
  grant.
- Requiring application authors to install Node; requiring a durable cross-process
  audit store (`REV-026-003` stays accepted risk).
- Graduating the `/a11y` panel into `EXPLORER-019` / ATAG review workspace.
- Owning `hedron package doctor` (0.53) or conformance-kit / Node/Java evaluator
  authority (0.52).
- Mounting FastAPI `explorer_router` on Flask or Django.
- Closing `SR-021`, scheduling `1.0`, or promoting Beta package maturity.

## Proposed design

### Layers

```text
hedron-core          portable inspection models, redaction, trace read APIs,
                     ExplorerProvider v1, ExplorerPanelMeta compatibility
       │
hedron_explorer.services   catalog, simulation, traces, diff, view rendering
       │
       ├── thin HTTP router (/hedron-explorer/, frozen mount contract)
       ├── hedron CLI (inspect/graph/check — shared services when installed)
       └── first- and third-party ExplorerProvider panels
```

1. **`hedron-core`** owns portable inspection models, redaction, trace read APIs, and
   the provider protocol — no FastAPI imports.
2. **`hedron-explorer`** owns HTTP mounting, HTML shell, provider orchestration, and
   package-owned tests. It depends on `hedron-core` and FastAPI, not `hedron`.
3. **`hedron` CLI** may call the same services only when `hedron-explorer` is
   installed; absence is a labeled skip, not a FastAPI import into core.
4. **Mount contract frozen:** prefix `/hedron-explorer`,
   `explorer="off"|"development"|"secured"`, JSON prefix `/hedron-explorer/api/`,
   production forced-off for `development`.

### Consume shipped, do not fork

Stage 1 consumes these 0.49.1 symbols:

- `hedron.app.explorer.ExplorerMode`, `resolve_explorer_mode`,
  `mount_explorer_if_enabled`, `install_explorer_bridges`
- `hedron_explorer.router.explorer_router`, `explorer_guards` (120 req / 60s,
  `EXPLORER_DENIED`)
- `hedron_core.plugins.explorer.ExplorerPanelMeta` (`panel_id`, `title`, `plugin`,
  `description`, `path`), `register_explorer_panel`, `get_explorer_panels`
- `PluginContext.register_explorer_panel` (stamps `plugin=self.meta.name`)
- CSRF `hedron_csrf` / `X-CSRF-Token` / `X-Hedron-CSRF`
- `InteractionCatalog.to_manifest(profile="development")`, `handle_graph_payload`,
  `catalog_facts`, `included_bundles`
- CLI `hedron.cli.commands.{inspect,graph,check,routes}` and
  `hedron check --format sarif` via `diagnostics_to_sarif`
- Process-local `_AUDIT` (`REV-026-003`, maxlen 200) and `_TRACE` (maxlen 100)

### Provider protocol v1

`ExplorerProvider` is additive in `hedron-core`. Existing `path=` registrations remain
valid. First-party metadata-only panels stay:

| `panel_id` | `path` |
|---|---|
| `hedron-data-schema` | `/hedron-explorer/data` |
| `hedron-charts-viz` | `/hedron-explorer/charts` |
| `hedron-maps` | `/hedron-explorer/maps` |
| `hedron-extras-features` | `/hedron-explorer/packages` |
| `sample-kit-callout` | `/hedron-explorer/packages` |

Plugin `path=` does not add nav entries. Dedicated `/extras` is not shipped. Timeout,
ordering, redaction profile, and payload ceilings are new provider fields; spelling is
locked in [explorer-provider-050.toml](../acceptance/explorer-provider-050.toml).

### Query, diff, lab, and headless

QUERY-050 turns silent slices into pagination or truncation diagnostics. DIFF-050 diffs
catalog/manifest/route/schema fingerprints without a fourth fingerprint authority.
LAB-050 executes only `_SIMULATE_KEYS` (`route`, `allow_mutations`, `mode`, `target`,
`boosted`, `history_restore`, `status`), `/api/click-preview`, and
`/api/element-simulate` (`failure in {none,module,upgrade}`) with
`allow_mutations=false` by default. HEADLESS-050 reuses `diagnostics_to_sarif` and must
name today's graph-shape divergence (`inverse_consumers` on CLI, not Explorer).

## Alternatives considered

- **Rewrite Explorer as a Node SPA.** Rejected: application authors must not need Node;
  the shipped UI is server-rendered HTML plus one CSS file.
- **Replace `ExplorerPanelMeta` immediately.** Rejected: first-party plugins already
  register `path=`; provider is additive.
- **Mount Explorer on Flask/Django.** Rejected: hosts currently hard-set
  `explorer_mode="off"`; 0.50 adds labeled registry/catalog/CLI consumption only.
- **New Explorer SARIF writer.** Rejected: CLI already emits SARIF through
  `diagnostics_to_sarif`.

## Security implications

- Production + `development` remains forced off (`RISK_EXPLORER_DEVELOPMENT`).
- `secured` still requires `explorer_dependencies` or
  `request.state.hedron_authenticated` (401).
- Simulate stays allowlisted; mutations 403; CSRF names stay frozen unless
  SECURITY-050 explicitly changes them.
- Catalog presence never grants production authority.
- `REV-026-003` process-local `_AUDIT` is not SIEM.

## Accessibility implications

0.50 covers shell/panel keyboard, focus, landmark, reduced-motion, high-contrast,
narrow-viewport, and no-JavaScript behavior for Supported Explorer workflows. The
existing `/a11y` panel is not `EXPLORER-019`.

## Performance implications

Startup, first-render, query, memory, and maximum-payload budgets use small, medium,
and large registry fixtures. Unbounded document construction is forbidden. Cancellation
and backpressure apply to slow queries. Numeric budgets are Stage 1 evidence, not
Stage 0 invention.

## Testing strategy

Package-owned unit tests, Chromium/Firefox/WebKit journeys, a11y keyboard/no-JS,
adversarial simulate/provider-crash corpus, and 0.49.1 upgrade/rollback fixtures.
Gate scripts `scripts/check_*_050.py` are Stage 1; Stage 0 packet honesty is
`scripts/verify_pkg_50.py --allow-planned`.

## Compatibility and migration

Public 0.49.1 HTML and JSON paths stay. Adding panels is additive; renaming or removing
frozen routes is a `COMPAT-050` failure. `ExplorerPanelMeta` remains. Flask/Django stay
`projection_adapter` stacked on
[adapter-disposition-044.toml](../acceptance/adapter-disposition-044.toml) and
[host-portable-facts-045.toml](../acceptance/host-portable-facts-045.toml).

## Resolved questions (D-085)

1. **Which gates?** Closed inventory `ARCH-050`, `PROVIDER-050`, `CONSUME-050`,
   `QUERY-050`, `DIFF-050`, `LAB-050`, `HEADLESS-050`, `ECOSYSTEM-050`,
   `SECURITY-050`, `PRIVACY-050`, `A11Y-050`, `BROWSER-050`, `PERF-050`,
   `RESILIENCE-050`, `DOCS-050`, `COMPAT-050`, `REGRESS-050`, and `PKG-050`.
   Do not park provider protocol or headless parity later.
2. **Does Explorer become a production default?** No. Modes and production refusal
   stay. Presence in a catalog is not an authority grant.
3. **May live traces graduate in 0.50?** No. `EXPLORER-10-001` stays Deferred on
   `0.10.x`. Bounded historical `_TRACE` / simulate traces only.
4. **What is the release baseline?** Verified 0.49 is required before Stage 1 or the
   0.50 cut. **D-086** locks the living/planning baseline to Published in-tree
   `v0.49.1`.

## Resolved questions (D-086)

1. **Does 0.50 still include all 18 gates?** Yes. The D-085 list remains in scope.
   `EXPLORER-10-001` and `EXPLORER-019` stay explicitly Deferred outside this matrix.
2. **Does this refine change a later phase or the living tip?** No. Cut target stays
   `v0.50.0`. Living tip stays `v0.49.1`. Do not reopen 0.49, `polling_only`,
   `MORPH-048`, `SR-021`, or schedule `1.0`.
3. **Which shipped seams does 0.50 consume?** `explorer_router`, `ExplorerMode`
   `off`/`development`/`secured`, `resolve_explorer_mode` /
   `mount_explorer_if_enabled` / `install_explorer_bridges`, prefix
   `/hedron-explorer/`, `ExplorerPanelMeta` / `register_explorer_panel`,
   `explorer_guards`, `_SIMULATE_KEYS`, CSRF `hedron_csrf` / `X-CSRF-Token` /
   `X-Hedron-CSRF`, `InteractionCatalog.to_manifest(profile="development")`,
   `handle_graph_payload`, `catalog_facts`, `included_bundles`, CLI
   `inspect`/`graph`/`check`/`routes`, and `diagnostics_to_sarif`. Flask/Django
   hard-set `explorer_mode="off"`.
4. **Where does `ExplorerProvider` live?** Portable protocol in `hedron-core` (no
   FastAPI). HTTP/HTML stay in `hedron-explorer`. CLI in `hedron` may call shared
   services only when `hedron-explorer` is installed.
5. **Does `ExplorerPanelMeta` go away?** No. Provider is additive. Existing `path=`
   registrations remain valid.
6. **Is a thin `router.py` (~200 lines) permission to drop routes?** No. It is an
   `ARCH-050` module-boundary target plus a golden route map.
7. **What happens to silent `[:200]` slices?** QUERY-050 turns them into cursor
   pagination or typed truncation diagnostics, including a11y `[:40]`, audit `[:20]`,
   and `CacheTrace.recent(50)`.
8. **Does Explorer grow a SARIF writer?** No. HEADLESS-050 reuses
   `hedron check --format sarif` (`diagnostics_to_sarif`). Identity parity must name
   `inverse_consumers` divergence.
9. **What may the laboratory execute?** Only declared safe preview ops:
   `/api/simulate`, `/api/click-preview`, `/api/element-simulate`. No invented auth.
10. **Is package health `hedron package doctor`?** No. Read-only slice only; doctor
    stays 0.53.
11. **Is `/a11y` the ATAG workspace?** No. Keep the panel; `EXPLORER-019` stays
    Deferred.
12. **Reserve which diagnostics?** Reserve `HED-EXPLORER-*` in docs only at Stage 0.
    Do not add runtime symbols. Tracking [#501](https://github.com/eddiethedean/hedron/issues/501).
    In-tree Verified 0.49 is enough predecessor evidence; do not wait on PyPI/Git
    `#380` assets.

Locks: [explorer-architecture-050.toml](../acceptance/explorer-architecture-050.toml) ·
[explorer-provider-050.toml](../acceptance/explorer-provider-050.toml) ·
[explorer-query-050.toml](../acceptance/explorer-query-050.toml) ·
[explorer-diff-050.toml](../acceptance/explorer-diff-050.toml) ·
[explorer-lab-050.toml](../acceptance/explorer-lab-050.toml) ·
[explorer-headless-050.toml](../acceptance/explorer-headless-050.toml).

## Acceptance criteria

- RFC-0077 and D-085/D-086 are Accepted; tracking [#501](https://github.com/eddiethedean/hedron/issues/501) is bound.
- Stage 0 changes contracts only; no 0.50 runtime or version claim.
- Every 0.50-owned gate is Planned with an evidence command name; Stage 1 may not start
  until Verified 0.49 and this tracking issue exist.
- Frozen 0.49.1 mount, modes, HTML/JSON paths, and `ExplorerPanelMeta` remain named.
- Deferred items (`EXPLORER-10-001`, `EXPLORER-019`, `REV-026-003`) stay explicit.
