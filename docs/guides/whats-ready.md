# What’s ready today

**Canonical maturity snapshot for Hedron 0.27.x** (last published `v0.27.0`). Other
evaluator pages link here — do not treat parallel summaries as a second source of truth.
Maintainer evidence tables live in the repository
[`docs/STATUS.md`](https://github.com/eddiethedean/hedron/blob/main/docs/STATUS.md).

For a pinned internal admin/CRUD app on 0.27.x (`hedron>=0.27.0,<0.28`), you can use:
typed pages, HTMX fragments, CSRF (`standard`/`strict`), Flask/Django adapters,
and polling for job status.

Pin versions. Packages are Beta (no 1.0, no SLA). Prefer polling over SSE/WebSocket.

**Charts / sample kit:** install with floors
`hedron[charts]>=0.27.0,<0.28` and `hedron-sample-kit>=0.1.6,<0.2`.
Matplotlib/static charts are the **Supported** default path on the Alpha
`hedron-charts` package; Plotly / Altair remain **Experimental**.
**Experimental:** notebook, MCP, Gradio, live SSE/WS.

Need procurement detail (API stability tiers, a11y sessions, evidence)? See
[How labels work](#how-labels-work) below — skip it if you are just building.

!!! tip "Can I ship an internal admin app?"

    **Yes, with pins** — see the summary above. Walkthrough:
    [Build your first app](../getting-started/quickstart.md) →
    [HTMX interactions](htmx-interactions.md) →
    [Minimal form](minimal-form.md). Extras:
    [Installation](../getting-started/installation.md). Ship checklist:
    [Ship a Hedron app](ship.md).

Start building: [First app](../getting-started/quickstart.md). Evaluators:
[Evaluate Hedron](evaluate.md).

## How labels work

<details markdown>
<summary>Package Beta ≠ capability Supported ≠ API <code>stable</code> (evaluators)</summary>

**Supported** means the capability works on the current train when pinned. Most public
symbols remain API compatibility level **`beta`**. The
[minimal](../api/STABILITY.md#minimal-stable-tier) and
[expanded](../api/STABILITY.md#expanded-stable-tier-023) stable tables are
compatibility-protected today (narrow Beginner/CRUD facade —
[STABLE_FACADE](../api/STABLE_FACADE.md)) — not every Supported row on this page.
Package maturity remains **Beta** on PyPI — no scheduled 1.0, no commercial SLA.

| Label | Meaning |
|---|---|
| **Supported** | Working with pinned versions for the stated host — ship with pins; **≠** API `stable` |
| **Experimental** | Public API shipped; may change; prefer documented fallbacks (e.g. polling) |
| **Alpha** | On PyPI; pin and expect churn |
| **Deferred** | Documented, not ready — do not treat as Supported |

Package maturity (Beta/Alpha) ≠ capability readiness (Supported/Experimental/Deferred) ≠
API levels in [STABILITY](../api/STABILITY.md). Full cheat-sheet:
[Maturity labels (evaluators)](../getting-started/how-to-read.md).

Human accessibility testing protocol engineering is on the train; **compensated screen-reader
sessions are not Supported yet** — do not market human AT as done.

</details>

!!! warning "Live transports"

    SSE, focused streaming, WebSocket channels, and navigation preload are
    **experimental** (`hedron.experimental`). Prefer [polling](live-interaction.md) in
    production — see [LIVE_DISPOSITION](../api/LIVE_DISPOSITION.md).
    **This page is the only maturity source of truth** for Supported vs Experimental claims.

## Use today

| Job | Status | Start here |
|---|---|---|
| Ship CRUD / admin / forms | **Supported** | [First app](../getting-started/quickstart.md) → HTMX → Minimal form |
| Multi-worker durable jobs | **Supported** with shared Redis backend | [Jobs](../api/JOBS.md) · [Celery / RQ](jobs-celery-rq.md) |
| DataTable / DataEditor | **Supported** (`hedron[data]`) | [Data apps](data-apps.md) |
| Flask / Django host | **Supported** | [Flask](../getting-started/flask.md) · [Django](../getting-started/django.md) |
| Live SSE / WebSocket updates | **Experimental** | Prefer [polling](live-interaction.md) |
| Charts | **Supported** Matplotlib/static on Alpha package | Install `hedron[charts]>=0.27.0,<0.28`; Matplotlib/static is Supported; Plotly / Altair remain **Experimental** ([compatibility](../COMPATIBILITY.md#charts-and-sample-kit-compatibility-floor)) |
| Model demos / inference workflows | **Supported** capability (fail-closed; APIs `beta`) | Learn from [Model demos](model-demos.md) snippets — **no** Gradio-like product sample in-tree; evidence app is a [stub](https://github.com/eddiethedean/hedron/blob/main/examples/model-demo-0.18/README.md) |
| Notebook / MCP / Gradio | **Experimental** / **Alpha** | Pin extras; not production defaults |

!!! note "Package train vs capability"

    Flagship packages are **Beta** maturity — pin `hedron>=0.27.0,<0.28`. The table above is
    **capability readiness** (Supported / Experimental / Deferred), not package maturity.

<details markdown>
<summary>Full Supported / Experimental / Deferred matrices</summary>

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
| OIDC / session helpers + connection registry | `hedron` | Supported **helpers** (API `beta`); host auth/DI authoritative — **not** an IdP product |
| Curated extras toolkit (install-isolated) | `hedron[extras]` | Supported for the curated toolkit surface; **not** CodeEditor / TerminalView / joystick / device. Those surfaces require `hedron[experimental-ui]` plus `HEDRON_EXPERIMENTAL_UI` or explicit plugin enablement and remain importable from `hedron_extras.experimental` |
| Dashboard bindings, patches, cross-filter, AppShell | `hedron` / `hedron-core` | Supported (API `beta`; see [what's new 0.17](whats-new-0.17.md)) |
| Public `render_interaction` | `hedron` | Supported |
| Dialog / Tabs / Pagination / Lazy markup asserts | `hedron.testing` | Supported |
| `InferenceInterface` / `ModelDemo` / `ActionRegistry` | `hedron-core` / `hedron` | Supported capability; API level `beta`; fail-closed |
| Example sets, prediction labels, feedback, workflows | `hedron-core` / `hedron` | Supported capability; API level `beta`; consent mandatory for feedback |
| `InferencePolicy` / `ModelDemoScenario` | `hedron-core` | Supported capability; API level `beta`; in-process queue is dev-only |
| `InteractionRecorder` | `hedron` | Supported capability; API level `beta`; public endpoints only |
| Accessibility contracts / profile / claim boundaries | `hedron_core.a11y` | Supported capability; API `beta`; **no** auto WCAG/legal/VPAT claims — [A11Y](../api/A11Y.md) |
| Progressive-enhancement forms / landmarks / `Page(scripts=)` | `hedron` / `hedron-core` | Supported; HTMX is optional enhancement rather than a requirement for core form flows |
| Explorer accessibility workspace | `hedron[dev]` / `hedron-explorer` | Supported for local diagnostics (`/hedron-explorer/a11y`) |
| Automated Playwright/axe accessibility matrix | `hedron[browser]` | Supported automation evidence; **not equivalent to human assistive-technology testing** |

Pin package versions in production. “Supported” does not mean a commercial SLA or
guaranteed multi-worker live-transport proof.

## Experimental (prefer documented fallbacks)

| Capability | Package / surface | Notes |
|---|---|---|
| Live interaction: SSE, streaming, WebSocket, preload | `hedron.experimental` (FastAPI) | Prefer [polling](live-interaction.md) |
| CodeEditor | `hedron[experimental-ui]` | **Host stub** (CSP-safe shell; no pinned CodeMirror 6 bundle); importable from `hedron_extras.experimental`, but omitted from default plugin registration |
| Browser-Python sandbox | `hedron[extras]` | Origin-isolated; Experimental until you accept the isolation model |
| TerminalView / joystick / device bridges | `hedron[experimental-ui]` | Fail-closed experimental surfaces; omitted from default plugin registration but not blocked from direct Python imports |
| Native desktop shell | docs recipe | Packaging guidance only |
| Flask / Django live helpers | adapters | Prefer polling |

## Alpha / more volatile

| Package | Role |
|---|---|
| `hedron[charts]` / `hedron-charts` | Alpha package (`>=0.1.6,<0.2`); Matplotlib/static charts are the conservative default |
| `hedron[native]` / `hedron-native` | Optional Rust HTML-escape accel; pure-Python fallback Supported |
| `hedron[notebook]` / `hedron-notebook` | Localhost-oriented preview; not Supported production |
| `hedron[mcp]` / `hedron-mcp` | Deny-by-default MCP projection |
| `hedron[gradio]` / `hedron-gradio` | Gradio client interop; deny-by-default discover |
| `hedron-sample-kit` | Installable reference plugin (`>=0.1.6,<0.2`) |
| `packages/hedron-runtime-*` | Experimental Java / Node conformance runtimes |

## Deferred (do not market as Supported)

- Explorer live traces from the historical `0.10.x` work remain deferred.
- Compensated human screen-reader evaluation remains planned and is not Supported. The
  published evidence covers the protocol and automated Playwright/axe checks, not
  completed human sessions.

### Superseded in 0.24 (not Supported live)

- A full multi-engine live-browser matrix for FastAPI and adapters is not a Supported
  claim; the production recommendation is polling.
- Load/proxy backpressure evidence for live transports is incomplete; applications that
  opt into SSE/WebSocket must validate their own proxy and workload behavior.

Prefer [polling](live-interaction.md). Live SSE/WS helpers remain **experimental**.

Maintainer gate IDs and RFC evidence:
[`docs/STATUS.md`](https://github.com/eddiethedean/hedron/blob/main/docs/STATUS.md).

</details>

## Runnable examples

Prefer adopter recipes first:

- [Recipes](../examples/recipes/index.md) — Notes, session auth, uploads, jobs poll
- [Flask Refresh](../examples/flask-recipe.md) · [Django Refresh](../examples/django-recipe.md)
- FastAPI / Flask / Django reference apps — [runnable examples](../examples/runnable.md)

Phase-stamped folders (`data-app-0.15`, `dashboard-0.17`, `model-demo-0.18`, …) are
**maintainer evidence stubs**, not product tutorials — see
[phase evidence](../examples/phase-evidence.md). Live interaction sample:
[`examples/live-interaction`](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction)
(polling Supported; SSE/WS experimental).

## Recommended install

=== "uv (recommended)"

    ```bash
    uvx --from "hedron>=0.27.0,<0.28" hedron new my-app
    cd my-app && uv sync
    uv run uvicorn app:app --reload
    ```

=== "pip"

    ```bash
    pip install "hedron>=0.27.0,<0.28" "uvicorn[standard]"
    python -m hedron new my-app
    cd my-app && pip install -e .
    uvicorn app:app --reload
    ```

Pin `hedron>=0.27.0,<0.28` for the current published train.

Extras: `"hedron[data]>=0.27.0,<0.28"`, `"hedron[extras]>=0.27.0,<0.28"`,
`"hedron[jinja]>=0.27.0,<0.28"`, `"hedron[dev]>=0.27.0,<0.28"`,
`"hedron[notebook]>=0.27.0,<0.28"` (Alpha satellite),
`"hedron[mcp]>=0.27.0,<0.28"` (Alpha satellite),
`"hedron[gradio]>=0.27.0,<0.28"` (Alpha satellite),
`"hedron[charts]>=0.27.0,<0.28"`, and `"hedron-sample-kit>=0.1.6,<0.2"`.

## Role-specific wrappers

| Audience | Page |
|---|---|
| Quick fit check | [Evaluate Hedron](evaluate.md) |
| Ops ship checklist | [Ship a Hedron app](ship.md) · [Deployment](deployment.md) |
| Trust / maturity program | [Production-quality maturity](production-quality.md) |
| Security / procurement | [Enterprise diligence](enterprise-diligence.md) |

Also: [Upgrade](upgrade.md) · [Roadmap](roadmap.md) · [Live interaction](live-interaction.md)
