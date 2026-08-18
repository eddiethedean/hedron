# Phase 0.50 upgrade and rollback fixtures

**Status:** Planned for Stage 0 planning (0.49.1 baseline)<br>
**Planning baseline:** Published in-tree `v0.49.1`<br>
**Required predecessor/cut baseline:** Verified `v0.49.1`<br>
**Target:** Hedron `v0.50.0`<br>
**Decision/RFC:** D-085 / D-086 / [RFC-0077](../rfcs/RFC-0077-EXPLORER-ARCHITECTURE.md)<br>
**Tracking:** [#501](https://github.com/eddiethedean/hedron/issues/501)

Baseline JSON shape capture and rollback checks remain read-only during Stage 0.

## Mount and mode fixtures (0.49.1)

1. Prefix `/hedron-explorer/` via `include_router(..., prefix="/hedron-explorer")`.
2. Modes `off` / `development` / `secured` through `Hedron(..., explorer=)` and
   `[tool.hedron] explorer`.
3. Production + `development` → force `off` + `RISK_EXPLORER_DEVELOPMENT`.
4. `secured` without `explorer_dependencies` → `request.state.hedron_authenticated` (401).
5. Flask/Django `explorer_mode="off"` (no `explorer_router` mount).

## Frozen HTML paths

`GET` `/`, `/routes`, `/component/{name}`, `/graph`, `/security`, `/a11y`, `/cache`,
`/charts`, `/maps`, `/extensions`, `/data`, `/auto`, `/packages`, `/elements`,
`/elements/{logical_id}`, `/inventory`, `/settings`, `/interactions`, `/features`,
`/static/{asset_path}`.

## Frozen JSON paths

- `GET` `/api/routes`, `/api/security`, `/api/components`, `/api/graph`,
  `/api/handle-graph`, `/api/interactions`, `/api/dashboard-graph` (`stability: experimental`),
  `/api/click-preview`
- `POST` `/api/simulate` (`_SIMULATE_KEYS`; `allow_mutations` default false; mutations 403)
- `POST` `/api/element-simulate` (`failure in {none,module,upgrade}`)

HTML-only (no JSON twin today): `/a11y`, `/cache`, `/charts`, `/maps`, `/extensions`,
`/data`, `/auto`, `/packages`, `/elements`, `/inventory`, `/settings`, `/features`,
`/component/{name}`.

## Provider registry fixture

| `panel_id` | `path` |
|---|---|
| `hedron-data-schema` | `/hedron-explorer/data` |
| `hedron-charts-viz` | `/hedron-explorer/charts` |
| `hedron-maps` | `/hedron-explorer/maps` |
| `hedron-extras-features` | `/hedron-explorer/packages` |
| `sample-kit-callout` | `/hedron-explorer/packages` |

`ExplorerPanelMeta` fields stay `panel_id`, `title`, `plugin`, `description`, `path`.
Plugin `path=` does not add nav.

## Fingerprint and headless fixtures

Catalog/manifest/route/schema fingerprints used by DIFF-050 and HEADLESS-050.
CLI `hedron inspect` / `graph` / `check --format sarif` (`diagnostics_to_sarif`) and
Explorer HTML/JSON must later agree on identities, severity, and redaction.
Known 0.49.1 divergence: CLI graph includes `inverse_consumers`; Explorer omits it.

## Large-app and laboratory fixtures

- Large-registry fixture: at least 2,000 components or a documented equivalent
  (today's silent cap is components `[:200]`).
- Also name a11y `[:40]`, `audit_tail[:20]`, `CacheTrace.recent(50)`, `_AUDIT`
  maxlen 200, `_TRACE` maxlen 100.
- Safe-ops laboratory: exported redacted `AppScenario` plus provider-failure handling.
  No invented auth.

## Rollback

Removing or renaming a frozen 0.49.1 path, dropping `ExplorerPanelMeta`, mounting
Explorer on Flask/Django, or treating catalog presence as authority is a
`COMPAT-050` failure. Workspace version stays `0.49.1` for this Stage 0 packet.
