# Explorer architecture and operator-grade development tooling (`v0.50`)

**Status:** Published in-tree `v0.50.0`; tag/PyPI deferred. Human AT (`SR-021`) stays open.<br>
**Tracking:** [#501](https://github.com/eddiethedean/hedron/issues/501)<br>
**Related:** [#496](https://github.com/eddiethedean/hedron/issues/496)–[#500](https://github.com/eddiethedean/hedron/issues/500) /
[#502](https://github.com/eddiethedean/hedron/issues/502) /
[#503](https://github.com/eddiethedean/hedron/issues/503)<br>
**Decision/RFC:** D-085, refined by D-086 / [RFC-0077](../rfcs/RFC-0077-EXPLORER-ARCHITECTURE.md)<br>
**Planning baseline:** Published in-tree `v0.49.1`<br>
**Target:** Hedron `v0.50.0`<br>
**Required predecessor:** Verified `v0.49.1`

Stage 1 shipped on the in-tree `v0.50.0` cut. [#501](https://github.com/eddiethedean/hedron/issues/501)
stays open until publish assets exist.

## Consume shipped, do not fork

- `hedron.app.explorer.ExplorerMode` (`off` / `development` / `secured`),
  `resolve_explorer_mode`, `mount_explorer_if_enabled`, `install_explorer_bridges`.
  Prefix `/hedron-explorer`. Production + `development` force off
  (`RISK_EXPLORER_DEVELOPMENT`). Flask/Django hard-set `explorer_mode="off"`.
- `hedron_explorer.router.explorer_router` (thin factory; services/views split), `explorer_guards`
  (120 req / 60s, `EXPLORER_DENIED`), `include_in_schema=False`.
- `ExplorerPanelMeta` / `register_explorer_panel` / `get_explorer_panels` in
  `hedron_core.plugins.explorer`. Fields: `panel_id`, `title`, `plugin`,
  `description`, `path`.
- Frozen HTML and JSON paths in
  [explorer-architecture-050.toml](../acceptance/explorer-architecture-050.toml).
- `_SIMULATE_KEYS`, CSRF `hedron_csrf` / `X-CSRF-Token` / `X-Hedron-CSRF`.
- `InteractionCatalog.to_manifest(profile="development")`, `handle_graph_payload`,
  `catalog_facts`, `included_bundles`.
- CLI `hedron inspect` / `graph` / `check` / `routes` import `hedron_explorer.services`
  when the extra is installed (labeled skip otherwise). SARIF is
  `hedron check --format sarif` via `diagnostics_to_sarif`.
- `_AUDIT` maxlen 200 (`REV-026-003`), `_TRACE` maxlen 100.
- Do **not** reopen `polling_only`, `MORPH-048`, `EXPLORER-10-001`, or
  `EXPLORER-019`.

Lock files: [explorer-architecture-050.toml](../acceptance/explorer-architecture-050.toml),
[explorer-provider-050.toml](../acceptance/explorer-provider-050.toml),
[explorer-query-050.toml](../acceptance/explorer-query-050.toml),
[explorer-diff-050.toml](../acceptance/explorer-diff-050.toml),
[explorer-lab-050.toml](../acceptance/explorer-lab-050.toml),
[explorer-headless-050.toml](../acceptance/explorer-headless-050.toml).

## Architecture

```text
hedron-core          portable inspection models, redaction, ExplorerProvider v1
       │
hedron_explorer.services   catalog, simulation, traces, diff, view rendering
       │
       ├── thin HTTP router (/hedron-explorer/, frozen mount contract)
       ├── hedron CLI (inspect/graph/check — shared services when installed)
       └── first- and third-party ExplorerProvider panels
```

1. Portable models and `ExplorerProvider` live in `hedron-core` (no FastAPI).
2. HTTP/HTML stay in `hedron-explorer`.
3. CLI in `hedron` may call shared services only when `hedron-explorer` is installed;
   absence is a labeled skip.
4. Authority stays 0.43 descriptor → 0.44 TypeSchema → 0.45 catalog. Explorer never
   becomes runtime authority.

## Work packages

### M1 — Baseline and inventory

- Golden route map from 0.49.1 HTML vs JSON paths.
- Capability inventory with Supported / Experimental / Excluded dispositions.
- Upgrade fixtures from `v0.49.1` mount URLs and JSON shapes.

### M2 — Service extraction

- Split into `services/catalog.py`, `services/simulation.py`, `services/traces.py`,
  `services/diff.py`, `views/`.
- Thin `router.py` (under 200 lines target) without dropping frozen routes.
- Contract tests preventing re-monolithization.

### M3 — Provider protocol v1

- Additive `ExplorerProvider` in `hedron-core`.
- Keep `ExplorerPanelMeta` / `register_explorer_panel`.
- Migrate first-party `path=` panels (data/charts/maps/extras/sample-kit).

### M4 — Query UX and resilience

- Search/filter/sort and cursor pagination or virtualization.
- Replace silent `[:200]` / a11y `[:40]` / audit `[:20]` / `CacheTrace.recent(50)`.
- Small/medium/large registry fixtures (large = 2,000+ or documented equivalent).

### M5 — Headless operator outputs

- Unify CLI on shared services when Explorer is installed.
- JSON export; reuse `diagnostics_to_sarif`; name `inverse_consumers` divergence.
- Baseline diff for catalog/manifest/routes/OpenAPI fingerprints.

### M6 — Interaction laboratory (bounded)

- TypeSchema v2 inputs; `/api/simulate`, `/api/click-preview`,
  `/api/element-simulate` only.
- Redacted `AppScenario` export; no invented auth.
- Read-only package health slice — not `hedron package doctor` (0.53).

### M7 — Evidence and docs

- Package-owned tests; Chromium/Firefox/WebKit; a11y keyboard/no-JS; security corpus.
- Provider author guide and 0.49 hook migration.
- Planned checker names `scripts/check_*_050.py` (Stage 1 bodies).

## Failure boundaries

- Wrong `HX-Target` / undeclared simulate keys fail closed.
- Provider timeout/crash isolates to that panel.
- Production + `development` refuses start (`RISK_EXPLORER_DEVELOPMENT`).
- Catalog presence is not an authorization grant.
- `REV-026-003` process-local `_AUDIT` is not durable SIEM.

## Diagnostics

Reserve `HED-EXPLORER-*` in docs only at Stage 0. Do not add runtime symbols.

## Stage ordering

Stage 0 (this document): contracts, locks, tracking [#501](https://github.com/eddiethedean/hedron/issues/501).
Companion authoring [#496](https://github.com/eddiethedean/hedron/issues/496)–[#500](https://github.com/eddiethedean/hedron/issues/500) /
[#502](https://github.com/eddiethedean/hedron/issues/502) /
[#503](https://github.com/eddiethedean/hedron/issues/503) are bound to the 0.50 train;
they are not Explorer gates and do not live in this module split.
Stage 1: implementation behind those locks. No living-tip bump in Stage 0.
