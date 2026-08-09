# Performance budgets

**Status:** Soft render budgets on the living train (introduced in phase 0.8;
still enforced). Phase **0.25** critical-path workloads (`BUDGET-025` / `W-025-*`)
have runnable CI evidence under `tests/performance/test_w025_*.py`.

**Evidence:** `PERF-08-001`, `PERF-08-002`, `tests/performance/`; `BUDGET-025` /
`W-025-*`.

Budgets are soft CI ceilings sized for GitHub-hosted runners. They catch gross regressions;
they are not marketing latency claims. Measure with `tests/performance/`.

Live SSE/WebSocket load/proxy backpressure IDs (`PERF-10-001` and related) were
**Superseded** in **0.25** under disposition `polling_only` — prefer
[polling](guides/live-interaction.md) in production. See
[What’s ready](guides/whats-ready.md), [LIVE_DISPOSITION](api/LIVE_DISPOSITION.md), and
[Performance guide](guides/performance.md).

## Workloads

| ID | Workload | Command |
|---|---|---|
| W-RENDER-200 | Normalize + serialize 200 text nodes | `pytest tests/performance -q` |
| W-PAGE | Full `RenderMode.PAGE` for a small Page | same |
| W-FRAGMENT | Fragment render for a small tree | same |
| W-PAYLOAD | HTML payload size for 200-node stack | same |

## Phase 0.25 critical-path workloads (`BUDGET-025`)

Runnable CI evidence paths (soft ceilings in the named tests):

| ID | Workload | evidence_path |
|---|---|---|
| W-025-FRAGMENT | Fragment latency under representative HTMX swap load | tests/performance/test_w025_fragment.py |
| W-025-JOB-POLL | Job status poll fanout | tests/performance/test_w025_job_poll.py |
| W-025-DATAEDITOR | DataEditor row-model smoke | tests/performance/test_w025_dataeditor.py |

Checker: `python scripts/check_budget_025.py`.

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
