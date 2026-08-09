# What’s ready today

**Canonical maturity snapshot for Hedron 0.25.0** (Published as `v0.25.0`). Other
evaluator pages link here — do not treat parallel summaries as a second source of truth.
Maintainer evidence tables live in the repository
[`docs/STATUS.md`](https://github.com/eddiethedean/hedron/blob/main/docs/STATUS.md).

**Ship today** (pin `hedron>=0.25.0,<0.26`): typed pages, HTMX fragments, CSRF profiles
(`standard` / `strict`), pluggable CSRF strategies / header merge / `CsrfField`,
Flask/Django adapters, polling job status, accessibility contracts / PE forms, and the
production security floor. Prefer **polling** for live status. Charts, notebook, MCP, and
Gradio are experimental / Alpha — expect churn. No commercial SLA and no scheduled 1.0.

Human accessibility testing protocol engineering is on the train; **compensated screen-reader
sessions are not Supported yet** — do not market human AT as done.

!!! note "Supported ≠ API `stable`"

    **Supported** means the capability works on the current train when pinned. Most public
    symbols remain API compatibility level **`beta`**. The
    [minimal](../api/STABILITY.md#minimal-stable-tier) and
    [expanded](../api/STABILITY.md#expanded-stable-tier-023) stable tables are
    compatibility-protected today (narrow Beginner/CRUD facade —
    [STABLE_FACADE](../api/STABLE_FACADE.md)) — not every Supported row on this page.
    Package maturity remains **Beta** on PyPI — no scheduled 1.0, no commercial SLA.

**Prefer polling** over SSE/WebSocket (`hedron.experimental`).

**Pin and expect churn:** charts, notebook, MCP, Gradio.

Start building: [First app](../getting-started/quickstart.md). Evaluators:
[Evaluate Hedron](evaluate.md). Maturity vocabulary:
[How to read](../getting-started/how-to-read.md).

!!! tip "Can I ship an internal admin app?"

    **Yes, with pins** — see the summary above. Walkthrough:
    [Build your first app](../getting-started/quickstart.md) →
    [HTMX interactions](htmx-interactions.md) →
    [Minimal form](minimal-form.md). Extras:
    [Installation](../getting-started/installation.md).

<details markdown>
<summary>How to read labels on this page</summary>

Hedron **0.25.0** packages are **Beta** maturity (API `beta` unless noted in
[STABILITY.md](../api/STABILITY.md)). Expect occasional breaking changes on
`0.x` under the [compatibility policy](../COMPATIBILITY.md).

| Label | Meaning |
|---|---|
| **Supported** | Working with pinned versions for the stated host — ship with pins; **≠** API `stable` |
| **Experimental** | Public API shipped; may change; prefer documented fallbacks (e.g. polling) |
| **Alpha** | On PyPI; pin and expect churn |
| **Deferred** | Documented, not ready — do not treat as Supported |

Package maturity (Beta/Alpha) ≠ capability readiness (Supported/Experimental/Deferred) ≠
API levels in [STABILITY](../api/STABILITY.md). Full cheat-sheet:
[Understanding maturity labels](../getting-started/how-to-read.md).

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
| Charts | **Alpha** package (`hedron[charts]`) | Pin `hedron[charts]`; **Matplotlib** adapter path is the conservative **Supported** charts default; **Plotly** / **Altair** remain **experimental** (package Alpha ≠ Plotly Supported) until pins + CSP + a11y match DataTable ([CHARTS-025](../api/PRODUCTION_ARCHETYPE.md#charts-graduation-path-charts-025)) |
| Model demos / inference workflows | **Supported** capability (fail-closed; APIs `beta`) | Learn from [Model demos](model-demos.md) snippets — **no** Gradio-like product sample in-tree; evidence app is a [stub](https://github.com/eddiethedean/hedron/blob/main/examples/model-demo-0.18/README.md) |
| Notebook / MCP / Gradio | **Experimental** / **Alpha** | Pin extras; not production defaults |

!!! note "Package train vs capability"

    Flagship packages are **Beta** maturity — pin `hedron>=0.25.0,<0.26`. The table above is
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
| Curated extras toolkit (install-isolated) | `hedron[extras]` | Supported for the curated toolkit surface; **not** CodeEditor / TerminalView / joystick / device (quarantined to `hedron[experimental-ui]`, EXTRAS-025) |
| Dashboard bindings, patches, cross-filter, AppShell | `hedron` / `hedron-core` | Supported (API `beta`; see [what's new 0.17](whats-new-0.17.md)) |
| Public `render_interaction` | `hedron` | Supported |
| Dialog / Tabs / Pagination / Lazy markup asserts | `hedron.testing` | Supported |
| `InferenceInterface` / `ModelDemo` / `ActionRegistry` | `hedron-core` / `hedron` | Supported capability; API level `beta`; fail-closed |
| Example sets, prediction labels, feedback, workflows | `hedron-core` / `hedron` | Supported capability; API level `beta`; consent mandatory for feedback |
| `InferencePolicy` / `ModelDemoScenario` | `hedron-core` | Supported capability; API level `beta`; in-process queue is dev-only |
| `InteractionRecorder` | `hedron` | Supported capability; API level `beta`; public endpoints only |
| Accessibility contracts / profile / claim boundaries | `hedron_core.a11y` | Supported capability; API `beta`; **no** auto WCAG/legal/VPAT claims — [A11Y](../api/A11Y.md) |
| Progressive-enhancement forms / landmarks / `Page(scripts=)` | `hedron` / `hedron-core` | Supported (`PE-019` / `LANDMARK-019` / `SCRIPT-019`); HTMX optional |
| Explorer accessibility workspace | `hedron[dev]` / `hedron-explorer` | Supported for local diagnostics (`/hedron-explorer/a11y`) |
| Automated Playwright/axe AT matrix (`AT-019`) | `hedron[browser]` | Supported automation evidence; **≠** human AT |

Pin package versions in production. “Supported” does not mean a commercial SLA or
guaranteed multi-worker live-transport proof.

## Experimental (prefer documented fallbacks)

| Capability | Package / surface | Notes |
|---|---|---|
| Live interaction: SSE, streaming, WebSocket, preload | `hedron.experimental` (FastAPI) | Prefer [polling](live-interaction.md) |
| CodeEditor | `hedron[experimental-ui]` | **Host stub** (CSP-safe shell; no pinned CodeMirror 6 bundle) — experimental landmine; not part of `hedron[extras]` product UI |
| Browser-Python sandbox | `hedron[extras]` | Origin-isolated; Experimental until you accept the isolation model |
| TerminalView / joystick / device bridges | `hedron[experimental-ui]` | Fail-closed experimental landmines (EXTRAS-025 quarantine) |
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

- Explorer live traces (`EXPLORER-10-001` on `0.10.x`)
- Human screen-reader / compensated AT evaluation (**0.21** D-052: protocol Verified;
  `SR-021` / `PARTICIPANT-021` Planned — not Supported; `AT-019` on 0.19 is automated
  Playwright/axe only)

### Superseded in 0.24 (not Supported live)

- Full multi-engine live browser matrix for FastAPI and adapters (`BROWSER-10-001` /
  `LIVE-011-BROWSER`) — closed via `polling_only` / `BROWSER-024`
- Load/proxy backpressure evidence for live transports (`PERF-10-001`) — closed via
  `polling_only` / `PERF-024`

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
    uvx --from "hedron>=0.25.0,<0.26" hedron new my-app
    cd my-app && uv sync
    uv run uvicorn app:app --reload
    ```

=== "pip"

    ```bash
    pip install "hedron>=0.25.0,<0.26" "uvicorn[standard]"
    python -m hedron new my-app
    cd my-app && pip install -e .
    uvicorn app:app --reload
    ```

Pin `hedron>=0.25.0,<0.26` for the current published train.

Extras: `"hedron[data]>=0.25.0,<0.26"`, `"hedron[charts]>=0.1.0,<0.2"` (Alpha),
`"hedron[extras]>=0.25.0,<0.26"`, `"hedron[jinja]>=0.25.0,<0.26"`, `"hedron[dev]>=0.25.0,<0.26"`,
`"hedron[notebook]>=0.1.0,<0.2"` (Alpha), `"hedron[mcp]>=0.1.0,<0.2"` (Alpha),
`"hedron[gradio]>=0.1.0,<0.2"` (Alpha).

## Role-specific wrappers

| Audience | Page |
|---|---|
| Quick fit check | [Evaluate Hedron](evaluate.md) |
| Ops ship checklist | [Production readiness](production-readiness.md) |
| Trust / maturity program | [Production-quality maturity](production-quality.md) |
| Security / procurement | [Enterprise diligence](enterprise-diligence.md) |

Also: [Upgrade](upgrade.md) · [Roadmap](roadmap.md) · [Live interaction](live-interaction.md)
