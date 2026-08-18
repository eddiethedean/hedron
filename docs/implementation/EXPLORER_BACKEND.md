# Explorer backend implementation

## Architecture

The backend is an optional development router over sanitized registry views and trace stores. It never imports application modules from user-supplied names or reads arbitrary paths. Preview and request operations reference registered identifiers only.

**Shipped (0.50.0):** thin FastAPI `hedron_explorer.router.explorer_router` (factory +
`Depends(explorer_guards)` + one-liner handlers) over `services/` (catalog, simulation,
traces, diff, fs, query, provider, health, runtime) and `views/` (shell, pages).
`hedron.app.explorer` mount helpers stay frozen. Process-local `_AUDIT` (maxlen 200;
`REV-026-003` accepted risk) and `_TRACE` (maxlen 100) are not durable SIEM.

**Not in 0.50:** live SSE/WS traces (`EXPLORER-10-001`), ATAG workspace, Flask/Django
`explorer_router` mount, `hedron package doctor` (0.53). Contracts:
[RFC-0077](../rfcs/RFC-0077-EXPLORER-ARCHITECTURE.md), [EXPLORER_050](EXPLORER_050.md).

## Services

Shipped:

- Component, route, asset, style, plugin, and example queries (HTML tables; JSON for a subset of panels).
- Addressable-resource request simulation through allowlisted `/api/simulate` (not a live application test transport).
- Cache traces via `CacheTrace.recent` with cursor pagination / truncation diagnostics; static security findings; a11y contract listing with typed caps.
- Shared CLI/Explorer query services when `hedron-explorer` is installed (labeled skip otherwise).
- Additive `ExplorerProvider` v1 isolation (timeout/crash/payload/ordering/redaction).

Not shipped: live traces; performance-trace panel as a production default; `hedron package doctor`.

Mutation simulation is disabled by default. Example data sources are isolated from production persistence unless an explicit authenticated configuration says otherwise.

## Production policy

The router is not registered outside development by default. Production mode requires a separate authorization dependency, rate limits, audit events, strict redaction, restricted headers, and explicit operation allowlists. `explorer="development"` is forced off in production (`RISK_EXPLORER_DEVELOPMENT`). Flask/Django set `explorer_mode="off"` and do not mount `explorer_router`.

## Verification

Test absence in production, authorization, registry-only addressing, redaction, path and URL injection, dependency override isolation, mutation policy, trace bounds, and parity between preview and application rendering. 0.50 evidence IDs live in [release-gate-0.50.toml](../acceptance/release-gate-0.50.toml).
