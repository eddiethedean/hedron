# What’s ready today

**Canonical maturity snapshot for Hedron 0.18.0.** Other evaluator pages link here —
do not treat parallel summaries as a second source of truth. Maintainer evidence tables
live in the repository
[`docs/STATUS.md`](https://github.com/eddiethedean/hedron/blob/main/docs/STATUS.md).

!!! tip "Can I ship an internal admin app?"

    **Yes, with pins:** typed pages, HTMX fragments, CSRF (`standard` / `strict`), and
    **polling** job status on FastAPI (Flask/Django adapters Supported). Start with
    [Installation](../getting-started/installation.md) →
    [HTMX interactions](htmx-interactions.md) →
    [Minimal form](minimal-form.md).

    **Not for production live push yet:** SSE / WebSocket (`hedron.experimental`) —
    prefer [polling](live-interaction.md).

    **Pin and expect churn:** charts, notebook, MCP, Gradio (Alpha / Experimental).

    No commercial SLA and no scheduled 1.0. Evaluators: [Evaluate Hedron](evaluate.md).

## How to read this page

Hedron **0.18.0** packages are **Beta** on PyPI. Expect occasional breaking changes on
`0.x` under the [compatibility policy](../COMPATIBILITY.md).

| Label | Meaning |
|---|---|
| **Supported** | Working with pinned versions for the stated host — ship with pins |
| **Experimental** | Public API shipped; may change; prefer documented fallbacks (e.g. polling) |
| **Alpha** | On PyPI; pin and expect churn |
| **Deferred** | Documented, not ready — do not treat as Supported |

Do not combine labels (never pair Supported with a package Beta tag in one phrase).
Package maturity is **Beta** or **Alpha** on PyPI; capability readiness is **Supported**,
**Experimental**, or **Deferred**.
See [Understanding maturity labels](../getting-started/how-to-read.md).

!!! warning "Live transports"

    SSE, focused streaming, WebSocket channels, and navigation preload are
    **experimental** (`hedron.experimental`). Prefer [polling](live-interaction.md) in
    production until your own load/proxy evidence covers backpressure.
    **This page is the only maturity source of truth** for Supported vs Experimental claims.

## Use today

| Job | Status | Start here |
|---|---|---|
| Ship CRUD / admin / forms | **Supported** | [Installation](../getting-started/installation.md) → HTMX → Minimal form |
| Multi-worker durable jobs | **Supported** with shared Redis backend | [Jobs](../api/JOBS.md) · [Celery / RQ](jobs-celery-rq.md) |
| DataTable / DataEditor | **Supported** (`hedron[data]`) | [Data apps](data-apps.md) |
| Flask / Django host | **Supported** | [Flask](../getting-started/flask.md) · [Django](../getting-started/django.md) |
| Live SSE / WebSocket updates | **Experimental** | Prefer [polling](live-interaction.md) |
| Charts | **Alpha** | Pin `hedron[charts]`; Matplotlib default |
| Model demos / inference workflows | **Supported** (fail-closed) | [Model demos](model-demos.md) |
| Notebook / MCP / Gradio | **Experimental** / **Alpha** | Pin extras; not production defaults |

!!! note "Package train vs capability"

    Flagship packages are **Beta** on PyPI — pin `>=0.18.0,<0.19`. The table above is
    **capability readiness** (Supported / Experimental / Deferred), not package maturity.

## Supported capabilities

| Capability | Package / surface | Status |
|---|---|---|
| Typed pages, fragments, built-ins | `hedron` + `hedron-core` | Supported |
| FastAPI routing, CSRF profiles, CLI, testing helpers | `hedron` | Supported |
| HTMX fragment loops, `InteractionResult` | `hedron` | Supported |
| Chat / Dialog surfaces | `hedron` | Supported; history application-owned |
| Flask Blueprint / `init_app` | `hedron-flask` | Supported; live helpers Experimental (prefer polling) |
| Django AppConfig, forms bridge, QuerySet DataSource | `hedron-django` + `hedron-data` | Supported |
| Portable adapter test harness | `hedron_core.testing` / `hedron.testing.adapters` | Supported |
| Optional HDJ (`.hdj`) templates | `hedron[jinja]` | Supported |
| Celery / RQ `JobBackend` bridges | `hedron_core.jobs_celery` / `jobs_rq` | Supported; **require shared Redis** for multi-worker status |
| Component `prepare()` + adaptive concurrency | `hedron-core` / `hedron` | Supported |
| Optional distributed tracing | `hedron[otel]` / `hedron.tracing` | Supported optional |
| Security audit sink | `hedron_core.audit` | Supported |
| Auto (inspectable object rendering) | `hedron` (no extra) | Supported |
| DataTable / DataEditor + column catalog, views, TransformPlan | `hedron[data]` | Supported |
| AG Grid Community client + infinite row models | `hedron-data[aggrid]` | Supported; Enterprise out of scope |
| Dask / Snowflake bounded sources | `hedron-data[dask]` / `[snowflake]` | Supported |
| Component Explorer (dev) | `hedron[dev]` | Supported for local diagnostics |
| Language-neutral conformance kit | `hedron[conformance]` | Supported |
| HDJ loop/macro budgets, a11y static checks | `hedron[jinja]` | Supported |
| AppScenario + HTMX InteractionResult asserts | `hedron.testing` | Supported |
| `region` / `@fragment` / `swap` ergonomics | `hedron` | Supported |
| Typed controls, surface chrome, Map, media Range | `hedron` / `hedron-core` | Supported |
| CameraCapture / MicrophoneCapture | `hedron` / `hedron-core` | Supported with permission/retention policy |
| BrowserContext/Storage, Math, IFrame | `hedron` / `hedron-core` | Supported |
| OIDC / session helpers + connection registry | `hedron` | Supported helpers; host auth/DI authoritative |
| Curated extras / workbenches / editors | `hedron[extras]` | Supported; install-isolated |
| Browser-Python sandbox | `hedron[extras]` | Supported; origin-isolated |
| Dashboard bindings, patches, cross-filter, AppShell | `hedron` / `hedron-core` | Supported |
| Public `render_interaction` | `hedron` | Supported |
| Dialog / Tabs / Pagination / Lazy markup asserts | `hedron.testing` | Supported |
| `InferenceInterface` / `ModelDemo` / `ActionRegistry` | `hedron-core` / `hedron` | Supported; fail-closed |
| Example sets, prediction labels, feedback, workflows | `hedron-core` / `hedron` | Supported; consent mandatory for feedback |
| `InferencePolicy` / `ModelDemoScenario` | `hedron-core` | Supported; in-process queue is dev-only |
| `InteractionRecorder` | `hedron` | Supported; public endpoints only |

Pin package versions in production. “Supported” does not mean a commercial SLA or
guaranteed multi-worker live-transport proof.

## Experimental (prefer documented fallbacks)

| Capability | Package / surface | Notes |
|---|---|---|
| Live interaction: SSE, streaming, WebSocket, preload | `hedron.experimental` (FastAPI) | Prefer [polling](live-interaction.md) |
| TerminalView / joystick / device bridges | `hedron[extras]` | Fail-closed |
| Native desktop shell | docs recipe | Packaging guidance only |
| Flask / Django live helpers | adapters | Prefer polling |

## Alpha / more volatile

| Package | Role |
|---|---|
| `hedron[charts]` / `hedron-charts` | Chart adapters — pin; Matplotlib is the conservative default |
| `hedron[native]` / `hedron-native` | Optional Rust HTML-escape accel; pure-Python fallback Supported |
| `hedron[notebook]` / `hedron-notebook` | Localhost-oriented preview; not Supported production |
| `hedron[mcp]` / `hedron-mcp` | Deny-by-default MCP projection |
| `hedron[gradio]` / `hedron-gradio` | Gradio client interop; deny-by-default discover |
| `hedron-sample-kit` | Plugin sample |
| `packages/hedron-runtime-*` | Experimental Java / Node conformance runtimes |

## Deferred (do not market as Supported)

- Full multi-engine live browser matrix for FastAPI and adapters
- Load/proxy backpressure evidence for live transports
- Some Explorer live traces

Maintainer gate IDs and RFC evidence:
[`docs/STATUS.md`](https://github.com/eddiethedean/hedron/blob/main/docs/STATUS.md).

## Runnable examples

- FastAPI / Flask / Django reference apps — [runnable examples](../examples/runnable.md)
- Model-demo / inference workflow:
  [`examples/model-demo-0.18`](https://github.com/eddiethedean/hedron/tree/main/examples/model-demo-0.18)
  · [Model demos](model-demos.md)
- Dashboard / agent-interface:
  [`examples/dashboard-0.17`](https://github.com/eddiethedean/hedron/tree/main/examples/dashboard-0.17)
- Data-app surfaces:
  [`examples/data-app-0.15`](https://github.com/eddiethedean/hedron/tree/main/examples/data-app-0.15)
  · [`examples/data-app-0.16`](https://github.com/eddiethedean/hedron/tree/main/examples/data-app-0.16)
- Live interaction (poll + experimental demos):
  [`examples/live-interaction`](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction)

## Recommended install

=== "uv (recommended)"

    ```bash
    uvx --from "hedron>=0.18.0" hedron new my-app
    cd my-app && uv sync
    uv run uvicorn app:app --reload
    ```

=== "pip"

    ```bash
    pip install "hedron>=0.18.0" "uvicorn[standard]"
    python -m hedron new my-app
    cd my-app && pip install -e .
    uvicorn app:app --reload
    ```

Extras: `"hedron[data]>=0.18.0"`, `"hedron[charts]>=0.1.0"` (Alpha),
`"hedron[extras]>=0.18.0"`, `"hedron[jinja]>=0.18.0"`, `"hedron[dev]>=0.18.0"`,
`"hedron[notebook]>=0.1.0"` (Alpha), `"hedron[mcp]>=0.1.0"` (Alpha),
`"hedron[gradio]>=0.1.0"` (Alpha).

## Role-specific wrappers

| Audience | Page |
|---|---|
| Quick fit check | [Evaluate Hedron](evaluate.md) |
| Ops ship checklist | [Production readiness](production-readiness.md) |
| Security / procurement | [Enterprise diligence](enterprise-diligence.md) |

Also: [Upgrade](upgrade.md) · [Roadmap](roadmap.md) · [Live interaction](live-interaction.md)
