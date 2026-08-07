# Performance budgets

**Status:** Ready to cut on the **0.20** train (budgets introduced in phase 0.8; still
enforced; last published PyPI/git = `v0.19.0`)  
**Evidence:** `PERF-08-001`, `PERF-08-002`, `tests/performance/`

Budgets are soft CI ceilings sized for GitHub-hosted runners. They catch gross regressions;
they are not marketing latency claims. Measure with `tests/performance/`.

Load/proxy backpressure proof for live SSE/WebSocket remains **Deferred** — prefer
polling in production until you have your own ops evidence. See
[What’s ready](guides/whats-ready.md) and [Performance guide](guides/performance.md).

## Workloads

| ID | Workload | Command |
|---|---|---|
| W-RENDER-200 | Normalize + serialize 200 text nodes | `pytest tests/performance -q` |
| W-PAGE | Full `RenderMode.PAGE` for a small Page | same |
| W-FRAGMENT | Fragment render for a small tree | same |
| W-PAYLOAD | HTML payload size for 200-node stack | same |

## Budgets (CPython 3.12, ubuntu-latest)

| Metric | Budget | Notes |
|---|---|---|
| Tree normalize (200 nodes) | ≤ 250 ms | Soft CI ceiling |
| Serialize (200 nodes) | ≤ 250 ms | Soft CI ceiling |
| Full `render()` (200 nodes) | ≤ 500 ms | Includes normalize + serialize |
| Page HTML for small Page | ≤ 200 KiB | Document shell + HTMX script tag allowed |
| Fragment HTML for 200-node stack | ≤ 100 KiB | No document shell |
| Diagnostic JSON for ≤ 20 findings | ≤ 256 KiB | SARIF/text exporters |

## Adapter / ops (reference)

| Metric | Budget | Evidence location |
|---|---|---|
| Health endpoint | ≤ 100 ms local | `tests/ops/test_health.py` |
| Job status poll JSON | ≤ 64 KiB | job conformance |
| Chart SVG (Matplotlib smoke) | ≤ 1.5 MiB | chart security corpus |

## Enforcement

`tests/performance/test_budgets.py` fails the suite when a budget is breached. Hosts that
occasionally exceed soft ceilings should be investigated; do not silently raise budgets
without an owning decision and changelog note. (There is no automatic CI retry for these
tests.)
