# Performance

Application-oriented guidance. CI soft ceilings live in
[PERFORMANCE_BUDGETS.md](../PERFORMANCE_BUDGETS.md) (maintainer evidence), not as product
SLOs.

## Prefer fragments over full documents

HTMX fragment routes should return only the replaced region. Full `Page` responses on
every click inflate HTML, CSS, and HTMX processing cost.

## Bound live traffic

- Prefer [polling](live-interaction.md) with a clear stop condition for job UIs
- Treat SSE / WebSockets as best-effort observation; keep HTTP fallbacks
- Disable speculative [navigation preload](../api/PRELOAD.md) on authenticated mutation paths
- Watch reverse-proxy buffering for `text/event-stream`

## Cache consciously

Use typed `InteractionResult(cache=...)` (`private`, `no-store`, `vary-htmx`). Prefer
`vary-htmx` when one URL serves both documents and fragments. Do not mark authenticated
HTML `public`.

## Data and charts

- Install extras only when needed (`hedron[data]`, `hedron[charts]`)
- Bound `Auto` inspection; do not feed unbounded lazy queries into inference
- Paginate DataTable sources; avoid shipping entire datasets to the browser

## Process model

- Multiple uvicorn workers need sticky sessions or an external session store
- Redis (`HEDRON_REDIS_URL`) is only for job backends that require it—not for pages
- Keep CPU-heavy work off the request path (`JobBackend` / background tasks)

## Measure before optimizing

Record HTML size, fragment latency, and worker CPU for representative CRUD/admin flows.
Add complexity only when measurements justify it ([design principles](../foundations/03_DESIGN_PRINCIPLES.md)).

## See also

- [Deployment](deployment.md) · [Best practices](best-practices.md) · [Live interaction](live-interaction.md)
