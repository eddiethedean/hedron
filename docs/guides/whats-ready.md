# What’s ready today

**Canonical maturity snapshot for 0.13.0 (published).** Other evaluator pages link here —
do not treat parallel summaries as a second source of truth. Maintainer evidence tables
live in the repository
[`docs/STATUS.md`](https://github.com/eddiethedean/hedron/blob/main/docs/STATUS.md).

## How to read this page

Hedron **0.13.0** packages are **Beta**. There is no scheduled 1.0; expect occasional
breaking changes on `0.x` under the [compatibility policy](../COMPATIBILITY.md).

| Label | Meaning |
|---|---|
| **Supported** | Capability claimed working with pinned versions for the stated host |
| **Experimental** | Public API shipped; may change; prefer documented fallbacks (e.g. polling) |
| **Alpha** | Available on PyPI; pin and expect churn |
| **Deferred** | Documented, not ready — do not treat as Supported |

!!! warning "Live transports"

    SSE, focused streaming, WebSocket channels, and navigation preload are
    **experimental** (`hedron.experimental`). Prefer [polling](live-interaction.md) in
    production until ops gates (`PERF-10-001`, browser live matrices) close.

## Supported capabilities (Beta packages)

| Capability | Package / surface | Evidence note |
|---|---|---|
| Typed pages, fragments, built-ins | `hedron` + `hedron-core` | Supported |
| FastAPI routing, CSRF profiles, CLI, testing helpers | `hedron` | Supported |
| HTMX fragment loops, `InteractionResult` | `hedron` | Supported |
| Live interaction: SSE, streaming, WebSocket, preload | `hedron.experimental` (FastAPI) | **Experimental** — polling Supported |
| Chat/Dialog surfaces | `hedron` | Supported (beta); history application-owned |
| Flask Blueprint / `init_app` + live helpers | `hedron-flask` | Supported host; live helpers experimental; polling Supported |
| Django AppConfig, forms bridge, QuerySet DataSource | `hedron-django` + `hedron-data` | Supported |
| Portable adapter test harness | `hedron_core.testing` / `hedron.testing.adapters` | Supported |
| Optional HDJ (`.hdj`) templates + dynamic manifests / CSP inventory | `hedron[jinja]` | Supported |
| Celery / RQ `JobBackend` bridges | `hedron_core.jobs_celery` / `jobs_rq` | Supported optional bridges; **require shared Redis** for durable multi-worker status (0.13) |
| Component `prepare()` + adaptive concurrency | `hedron-core` / `hedron` | Supported (0.13); opt-out preserves semantics |
| Optional distributed tracing | `hedron[otel]` / `hedron.tracing` | Supported optional (0.13); disable anytime |
| Security audit sink | `hedron_core.audit` | Supported (0.13) |
| Auto (inspectable object rendering) | Core (`hedron`) — no extra | Supported |
| DataTable / DataEditor | `hedron[data]` | Supported |
| Column catalog, saved views, TransformPlan, typed grid events | `hedron[data]` | Supported (0.12) |
| Advanced DataEditor (formulas, pivots, trees, collab, spreadsheet I/O) | `hedron[data]` | Supported (0.12) |
| AG Grid Community client + infinite row models | `hedron-data[aggrid]` | Supported (0.12); Enterprise out of scope |
| Dask / Snowflake bounded sources | `hedron-data[dask]` / `[snowflake]` | Supported (0.12) |
| Beginner Area/Bar/Scatter + Plotly events/annotations | `hedron[charts]` | Alpha charts package |
| Optional viz adapters + offline runtime pins | `hedron[charts]` | Alpha; local-asset/CSP contracts |
| Component Explorer (dev) | `hedron[dev]` | Supported for local diagnostics; some live traces incomplete |

Pin package versions in production. “Supported” does not mean a commercial SLA or
guaranteed multi-worker live-transport proof — see
[STATUS](https://github.com/eddiethedean/hedron/blob/main/docs/STATUS.md) Deferred rows.

## Supported examples

- Live interaction sample (poll + token stream + SSE + Job SSE + WebSocket accept +
  preload):
  [`examples/live-interaction`](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction).
  Prefer polling behind load balancers until your own ops evidence covers SSE/WS
  backpressure ([live interaction guide](live-interaction.md)).
- FastAPI / Flask / Django reference apps — [runnable examples](../examples/runnable.md)

## Treat as Alpha / more volatile

- `hedron-charts` and chart backends
- `hedron-sample-kit` (plugin sample)

## Deferred (do not market as Supported)

- First-party camera/microphone capture UI → planned later (**0.15**)
- Full multi-engine live browser matrix for FastAPI and adapters
- Load/proxy backpressure evidence for live transports
- Some Explorer live traces

## Recommended install

```bash
pip install "hedron>=0.13.0" "uvicorn[standard]"
python -m hedron new my-app
cd my-app
pip install -e .   # or: uv sync
uvicorn app:app --reload
```

Extras: `"hedron[data]"`, `"hedron[charts]"` (Alpha), `"hedron[jinja]"`, `"hedron[dev]"`.

## Role-specific wrappers

| Audience | Page |
|---|---|
| Quick fit check | [Evaluate Hedron](evaluate.md) |
| Ops ship checklist | [Production readiness](production-readiness.md) |
| Security / procurement | [Enterprise diligence](enterprise-diligence.md) |

Also: [Upgrade](upgrade.md) · [Roadmap](roadmap.md) · [Live interaction](live-interaction.md)
