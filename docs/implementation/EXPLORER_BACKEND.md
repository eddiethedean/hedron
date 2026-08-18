# Explorer backend implementation

## Architecture

The backend is an optional development router over sanitized registry views and trace stores. It never imports application modules from user-supplied names or reads arbitrary paths. Preview and request operations reference registered identifiers only.

**Shipped (0.49.1):** one FastAPI module, `hedron_explorer.router.explorer_router` (~1,366 lines), plus `hedron.app.explorer` mount helpers. There is no `services/` layer. Process-local `_AUDIT` (maxlen 200; `REV-026-003` accepted risk) and `_TRACE` (maxlen 100) are not durable SIEM.

**Planned (0.50):** split catalog, simulation, traces, and diff into services behind a thin router, with `ExplorerProvider` v1 in `hedron-core`. Contracts: [RFC-0077](../rfcs/RFC-0077-EXPLORER-ARCHITECTURE.md), [EXPLORER_050](EXPLORER_050.md). Do not treat the bullets below as shipped if they are labeled 0.50.

## Services

Shipped:

- Component, route, asset, style, plugin, and example queries (HTML tables; JSON for a subset of panels).
- Addressable-resource request simulation through allowlisted `/api/simulate` (not a live application test transport).
- Cache traces via `CacheTrace.recent(50)`; static security findings; a11y contract listing `[:40]`.

0.50 targets (not shipped): isolated example rendering with FastAPI dependency overrides; performance-trace panel; build-result panel; shared CLI/Explorer query services.

Mutation simulation is disabled by default. Example data sources are isolated from production persistence unless an explicit authenticated configuration says otherwise.

## Production policy

The router is not registered outside development by default. Production mode requires a separate authorization dependency, rate limits, audit events, strict redaction, restricted headers, and explicit operation allowlists. `explorer="development"` is forced off in production (`RISK_EXPLORER_DEVELOPMENT`). Flask/Django set `explorer_mode="off"` and do not mount `explorer_router`.

## Verification

Test absence in production, authorization, registry-only addressing, redaction, path and URL injection, dependency override isolation, mutation policy, trace bounds, and parity between preview and application rendering. 0.50 evidence IDs live in [release-gate-0.50.toml](../acceptance/release-gate-0.50.toml).
