# What’s ready today

**Canonical maturity snapshot for 0.17.0.** Other evaluator pages link here —
do not treat parallel summaries as a second source of truth. Maintainer evidence tables
live in the repository
[`docs/STATUS.md`](https://github.com/eddiethedean/hedron/blob/main/docs/STATUS.md).

!!! tip "New here?"

    For a FastAPI CRUD / admin spike: typed pages, HTMX fragments, CSRF profiles, and
    polling are **Supported** on Beta packages — start with
    [Installation](../getting-started/installation.md). SSE/WebSocket live updates are
    **experimental**; prefer polling in production. Charts and native accel are **Alpha**.
    There is no commercial SLA and no scheduled 1.0. Evaluators: skim the table below, then
    [Evaluate Hedron](evaluate.md).

## How to read this page

Hedron **0.17.0** packages are **Beta**. There is no scheduled 1.0; expect occasional
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
    **This page is the only maturity SSOT** for Supported vs Experimental claims.

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
| Language-neutral conformance kit | `hedron[conformance]` / `hedron-conformance` | Supported (0.14) |
| Experimental Java / Node conformance runtimes | `packages/hedron-runtime-*` | **Experimental** / Alpha (0.14) |
| Optional Rust HTML escaping acceleration | `hedron[native]` / `hedron-native` | Alpha (0.14); pure-Python fallback Supported |
| HDJ loop/macro budgets, extension evidence, a11y static checks | `hedron[jinja]` | Supported (0.14; `HDJ-DEF-014`) |
| AppScenario + HTMX InteractionResult asserts | `hedron.testing` | Supported (0.15; #22–#26) |
| `region` / `@fragment` / `swap` ergonomics | `hedron` | Supported (0.15; RFC-0039) |
| Typed controls, surface chrome, Map, media Range | `hedron` / `hedron-core` | Supported (0.15) |
| CameraCapture / MicrophoneCapture | `hedron` / `hedron-core` | Supported (0.15; permission/retention policy explicit) |
| BrowserContext/Storage, Math, IFrame | `hedron` / `hedron-core` | Supported (0.15) |
| OIDC / session helpers + connection registry | `hedron` | Supported helpers (0.15); host auth/DI authoritative |
| Curated extras composition / workbenches / editors | `hedron[extras]` | Supported beta (0.16); install-isolated |
| TerminalView / joystick / device bridges | `hedron[extras]` | **Experimental** (0.16); fail-closed |
| Browser-Python sandbox | `hedron[extras]` | Supported beta (0.16); origin-isolated |
| Native desktop shell | docs recipe | **Experimental** packaging guidance only |
| `DashboardBinding` / `InteractionGraph` / `TriggerContext` | `hedron-core` / `hedron` | Supported beta (0.17; RFC-0040) |
| `PropertyPatch` / `CollectionPatch` | `hedron-core` | Supported beta (0.17; RFC-0041); full-fragment fallback mandatory |
| Cross-filter composition + graph recorder/replay | `hedron` / `hedron-core` | Supported beta (0.17) |
| `HtmxLink`/`NavLink`, `OobHost`/`AttrHost`, `AppShell`/`MainPanel` | `hedron` / `hedron-core` | Supported beta (0.17; RFC-0044) |
| Public `render_interaction` | `hedron` | Supported beta (0.17) |
| Dialog / Tabs / Pagination / Lazy markup asserts | `hedron.testing` | Supported (0.17; #24) |
| Notebook preview helper | `hedron[notebook]` / `hedron-notebook` | **Experimental** / Alpha (0.17) |
| MCP Streamable HTTP projection | `hedron[mcp]` / `hedron-mcp` | **Experimental** / Alpha (0.17); deny-by-default |

Pin package versions in production. “Supported” does not mean a commercial SLA or
guaranteed multi-worker live-transport proof — see
[STATUS](https://github.com/eddiethedean/hedron/blob/main/docs/STATUS.md) Deferred rows.

## Runnable examples

- FastAPI / Flask / Django reference apps — [runnable examples](../examples/runnable.md)
  (Supported host slices).
- 0.17 dashboard / agent-interface demo:
  [`examples/dashboard-0.17`](https://github.com/eddiethedean/hedron/tree/main/examples/dashboard-0.17).
- 0.15 data-app surface demo (`region` / `@fragment` / `swap`, controls, Map, media stubs):
  [`examples/data-app-0.15`](https://github.com/eddiethedean/hedron/tree/main/examples/data-app-0.15).
- 0.16 analysis workbench demo (`hedron-extras`):
  [`examples/data-app-0.16`](https://github.com/eddiethedean/hedron/tree/main/examples/data-app-0.16).
- Live interaction sample (poll + **experimental** token stream / SSE / Job SSE /
  WebSocket / preload demos):
  [`examples/live-interaction`](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction).
  Prefer polling behind load balancers until your own ops evidence covers SSE/WS
  backpressure ([live interaction guide](live-interaction.md)).

## Treat as Alpha / more volatile

- `hedron-charts` and chart backends
- `hedron-sample-kit` (plugin sample)
- `hedron-notebook` (localhost-oriented preview; not Supported production)
- `hedron-mcp` (deny-by-default; not Supported production tools by default)

## Deferred (do not market as Supported)

- Full multi-engine live browser matrix for FastAPI and adapters
- Load/proxy backpressure evidence for live transports
- Some Explorer live traces

## Recommended install

```bash
pip install "hedron>=0.17.0" "uvicorn[standard]"
python -m hedron new my-app
cd my-app
pip install -e .   # or: uv sync
uvicorn app:app --reload
```

Extras: `"hedron[data]"`, `"hedron[charts]"` (Alpha), `"hedron[extras]"`, `"hedron[jinja]"`,
`"hedron[dev]"`, `"hedron[notebook]"` (Alpha), `"hedron[mcp]"` (Alpha).

## Role-specific wrappers

| Audience | Page |
|---|---|
| Quick fit check | [Evaluate Hedron](evaluate.md) |
| Ops ship checklist | [Production readiness](production-readiness.md) |
| Security / procurement | [Enterprise diligence](enterprise-diligence.md) |

Also: [Upgrade](upgrade.md) · [Roadmap](roadmap.md) · [Live interaction](live-interaction.md)
