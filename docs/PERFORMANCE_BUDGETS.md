# Performance budgets

**Status:** Published soft render budgets on the **0.24** train (introduced in phase 0.8;
still enforced; last published PyPI/git = `v0.24.0`). Phase **0.25** adds critical-path
workloads (`BUDGET-025`) that are named here; runnable CI/artifact evidence remains
**Planned** until cut.

**Evidence:** `PERF-08-001`, `PERF-08-002`, `tests/performance/`; `BUDGET-025` /
`W-025-*` (packet refine complete; evidence Pending).

Budgets are soft CI ceilings sized for GitHub-hosted runners. They catch gross regressions;
they are not marketing latency claims. Measure with `tests/performance/`.

Live SSE/WebSocket load/proxy backpressure IDs (`PERF-10-001` and related) were
**Superseded** in **0.24** under disposition `polling_only` — prefer
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

Packet refine locked these IDs. Evidence may be **CI** or an **immutable artifact** at cut.
Until cut, `evidence_path` rows may be placeholders (`pending`).

| ID | Workload | evidence_path |
|---|---|---|
| W-025-FRAGMENT | Fragment latency under representative HTMX swap load | pending |
| W-025-JOB-POLL | Job status poll fanout | pending |
| W-025-DATAEDITOR | DataEditor row-model smoke | pending |

Checker: `python scripts/check_budget_025.py` (refine: `--allow-planned`).

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
