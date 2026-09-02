# Performance

Application-oriented guidance for the current **1.0.x** train. CI soft ceilings live in
[PERFORMANCE_BUDGETS.md](https://github.com/eddiethedean/hedron/blob/main/docs/PERFORMANCE_BUDGETS.md)
(maintainer evidence), not as product SLOs. Full load/proxy backpressure proof for SSE/WS
remains incomplete — prefer polling when that proof is required before you rely on live
transports in production.

!!! info "No public production benchmark baseline"

    Hedron does not currently publish a hardware-normalized requests-per-second or tail-latency
    claim. The repository budgets catch regressions on maintainer infrastructure; they are not
    capacity promises for an adopter application. Evaluate the exact component tree, middleware,
    database, worker model, and proxy topology you plan to ship.

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

Use `InteractionResult(cache=...)` (`private`, `no-store`, `vary-htmx`). Prefer
`vary-htmx` when one URL serves both documents and fragments. Do not mark authenticated
HTML `public`. Multi-tenant pages must include tenant (and usually user) dimensions in
cache keys — see [Threat model](threat-model.md).

## Data and charts

- Install `hedron[data]` only when needed. Charts require
  `hedron[charts]>=1.0.0` ([Compatibility](../COMPATIBILITY.md#charts-and-sample-kit-compatibility-floor))
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

Start with a small integration measurement around the actual route. Keep the assertion tied
to your application budget rather than treating Hedron's CI ceilings as an SLO:

```python
from time import perf_counter

from fastapi.testclient import TestClient

from app import app, status_view


def test_status_fragment_budget() -> None:
    with TestClient(app) as client:
        started = perf_counter()
        response = client.get(
            status_view.path,
            headers={"HX-Request": "true", "HX-Target": status_view.dom_id},
        )
        elapsed_ms = (perf_counter() - started) * 1_000

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert len(response.content) < 16_000
    assert elapsed_ms < 250  # Replace with a budget measured in your CI environment.
```

For stable timing data, warm the application first and collect a distribution across many
requests; the single-request form above is a readable regression guard, not a load test.

For an adoption benchmark, record at minimum: Python and package versions, CPU/memory limits,
worker count, route type (document or fragment), response bytes, data-store state, concurrency,
warm-up policy, p50/p95/p99 latency, errors, and the exact command used. Publish those inputs with
the result so another evaluator can reproduce it. Benchmark polling and live transports
separately because their connection and proxy costs are materially different.

## See also

- [Deployment](deployment.md) · [Best practices](best-practices.md) · [Live interaction](live-interaction.md) · [Observability](observability.md)

## Anti-patterns

- Returning a full `Page` for every HTMX click when a fragment region would do.
- Open-ended SSE/WebSocket streams without a stop condition or HTTP polling fallback.
- Marking authenticated HTML `public` or omitting tenant/user from cache keys.
- Shipping Plotly/Altair-heavy dashboards without pagination or server-side aggregation.
- Enabling Explorer or verbose diagnostics in production.

## Before you ship

Use the [Ship checklist](ship.md) and [Deployment](deployment.md). Treat CI performance
budgets as engineering signals, not customer SLOs.
