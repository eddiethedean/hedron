# Performance

Application-oriented guidance for the **0.19** train. CI soft ceilings live in
[PERFORMANCE_BUDGETS.md](https://github.com/eddiethedean/hedron/blob/main/docs/PERFORMANCE_BUDGETS.md)
(maintainer evidence), not as product SLOs. Full load/proxy backpressure proof for SSE/WS
remains incomplete — prefer polling when that proof is required before you rely on live
transports in production.

## Prefer fragments over full documents

HTMX fragment routes should return only the replaced region. Full `Page` responses on
every click inflate HTML, CSS, and HTMX processing cost.

## Bound live traffic

| Guidance | Why |
|---|---|
| Prefer [polling](live-interaction.md) with a clear stop condition for job UIs | Supported on every host; easier to size |
| Treat SSE / WebSockets as best-effort observation; keep HTTP fallbacks | Connection count and proxy buffering dominate |
| Disable speculative [navigation preload](../api/PRELOAD.md) on authenticated mutation paths | Avoid speculative authenticated GETs |
| Configure reverse-proxy buffering/timeouts for `text/event-stream` | Nginx/`proxy_buffering off`; long `proxy_read_timeout` |
| Cap concurrent EventSource / WS per user in the app | Hedron does not enforce a global connection budget |

### Capacity heuristics (until you have your own SSE/WS ops proof)

- Start with **one uvicorn worker** when debugging SSE/WS; then scale with sticky sessions.
- Expect each open SSE/WS to hold a worker slot / file descriptor — size workers and
  OS limits for peak concurrent observers, not just request rate.
- Prefer short-lived Job SSE streams that close on terminal state over infinite pings.
- Behind Kubernetes Ingress / ALB, disable response buffering for event-stream routes and
  raise idle timeouts above your longest expected observation window.

## Cache consciously

Use typed `InteractionResult(cache=...)` (`private`, `no-store`, `vary-htmx`). Prefer
`vary-htmx` when one URL serves both documents and fragments. Do not mark authenticated
HTML `public`. Multi-tenant pages must include tenant (and usually user) dimensions in
cache keys — see [Threat model](threat-model.md).

## Data and charts

- Install extras only when needed (`hedron[data]`, `hedron[charts]`)
- Bound `Auto` inspection; do not feed unbounded lazy queries into inference
- Paginate DataTable sources; avoid shipping entire datasets to the browser

## Process model

- Multiple uvicorn workers need sticky sessions or an external session store
- Redis (`HEDRON_REDIS_URL`) is only for job/cache backends that require it—not for pages
- Keep CPU-heavy work off the request path (`JobBackend` / background tasks)

## Measure before optimizing

Record HTML size, fragment latency, open SSE/WS count, and worker CPU for representative
CRUD/admin flows. Add complexity only when measurements justify it
([design principles](https://github.com/eddiethedean/hedron/blob/main/docs/foundations/03_DESIGN_PRINCIPLES.md)).

## See also

- [Deployment](deployment.md) · [Best practices](best-practices.md) · [Live interaction](live-interaction.md) · [Observability](observability.md)
