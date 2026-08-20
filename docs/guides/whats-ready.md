# What’s ready today

**Ship today (pinned CRUD / admin on FastAPI, Flask, or Django):** pages, HTMX
fragments, CSRF, polling job status, DataTable, first-party charts.
**Do not treat as production defaults:** SSE, WebSocket, Plotly/Altair, human
screen-reader claims. Packages are **Beta**. There is no SLA and no scheduled 1.0.

This page describes the living **0.54.x** train (in-tree tip **`v0.54.0`**). Git tag and
PyPI upload remain **deferred** — install from PyPI with `hedron>=0.54.0,<0.55` until the
0.53 wheel lands. Extras and public-index notes:
[Installation](../getting-started/installation.md). Capability
readiness, API compatibility, and package maturity are three
separate axes — [How labels work](#how-labels-work). Evaluators who need the cheat-sheet:
[Maturity labels](../getting-started/how-to-read.md).

Maintainer evidence tables live in the repository
[`docs/STATUS.md`](https://github.com/eddiethedean/hedron/blob/main/docs/STATUS.md).

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
| Refreshable views / command handles | **Supported** (API `beta`) | [Refreshable views](../api/REFRESHABLE_VIEWS.md) · [What’s new in 0.43](whats-new-0.43.md) |
| Type-driven authoring / generated forms | **Supported** (API `beta`) | [Type-driven authoring](../api/TYPE_DRIVEN_AUTHORING.md) · [What’s new in 0.44](whats-new-0.44.md) |
| Feature bundles / data workspaces | **Supported** (API `beta`; opt-in) | [Package workflows](../api/PACKAGE_WORKFLOWS.md) · [What’s new in 0.46](whats-new-0.46.md) |
| Declared HTMX extensions | **Supported** when declared and pinned (`sse`, `head-support`, `preload`); APIs for SSE/preload remain **experimental** | [HTMX extensions](../api/HTMX_EXTENSIONS.md) · [What’s new in 0.48](whats-new-0.48.md). Idiomorph is **Deferred** |
| First-class maps | **Supported** (API `beta`; `hedron[maps]`) | [Maps](../api/MAPS.md) · [What’s new in 0.47](whats-new-0.47.md) |
| Multi-worker durable jobs | **Supported** with shared Redis backend | [Jobs](../api/JOBS.md) · [Celery / RQ](jobs-celery-rq.md) |
| DataTable / DataEditor | **Supported** (`hedron[data]`; ABI `hedron-data-editor`) | [Data apps](data-apps.md) · [DATA.md](../api/DATA.md) |
| Bounded OptimisticMutation | **Supported** for collection/cell edits only; deny-by-default elsewhere | [DATA.md](../api/DATA.md) · [What’s new in 0.39](whats-new-0.39.md) |
| Public element author kit | **Supported** contracts (`hedron new element`, plugin registration) | [Plugin authoring](plugin-authoring.md) · [What’s new in 0.41](whats-new-0.41.md) · [What’s new in 0.42](whats-new-0.42.md) |
| ReactMigrationMatrix / island | Matrix **Supported** as guidance; island **Experimental** docs/reference only | [REACT_MIGRATION_MATRIX_040](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/REACT_MIGRATION_MATRIX_040.md) |
| Table↔chart cross-filter | **Supported** via `compose_chartlink_039` on Published 0.38 `hedron-chart` | [Dashboards](dashboards.md) |
| Flask / Django host | **Supported** | [Flask](../getting-started/flask.md) · [Django](../getting-started/django.md) |
| Posit Workbench / RStudio Server | **Supported** (`hedron[workbench]` or `hedron[posit]`) | [Posit Workbench](posit-workbench.md) · [Posit deployments](posit.md) — Workbench **2025.05.1**–**2026.07.0**; `HedronWorkbench` / `HedronPosit`; no import auto-wrap |
| Posit Connect (native GUID) | **Supported** (`hedron[posit]`) | [Posit deployments](posit.md) — Connect **2025.06.0**–**2026.07.0**; native cookies |
| Live SSE / WebSocket updates | **Experimental** | Prefer [polling](live-interaction.md) |
| Charts | **Supported** first-party and Matplotlib/static paths on Beta package | Install `hedron[charts]>=0.54.0,<0.55`; `ChartSpec` / `hedron-chart` and Matplotlib/static are Supported; Plotly / Altair remain **Experimental** ([Chart API](../api/CHART.md)) |
| Model demos / inference workflows | **Supported** capability (fail-closed; APIs `beta`) | Runnable [model-demo example](https://github.com/eddiethedean/hedron/tree/main/examples/model-demo-0.18) — [Model demos](model-demos.md) · [Recipes](../examples/recipes/index.md) |
| MCP projection | **Supported** inventory on Beta `hedron-mcp` `0.2.1` | Deny-by-default; pin `hedron[mcp]`; mutations Experimental |
| Notebook preview | **Supported tooling-grade scope** | Localhost preview only; not Supported production hosting |
| Remote Gradio / HF Space client interop | **Supported** on Beta `hedron-gradio` `0.2.0` | Declared allowlisted destinations; pin `>=0.2.0,<0.3`; [Gradio migration](gradio-migration.md) |
| Application DX Stage 1 | **Supported** (API `beta`; tip `v0.54.0`, tag/PyPI deferred) | Assets, diagnostics, routes, workflows, testgen, theming, discovery, fleet — [Application DX API](../api/APPLICATION_DX.md) · [What’s new in 0.53](whats-new-0.53.md) |
| Authoring loop / chrome (0.54) | **Supported** tooling-grade for notebook/sim/sample-kit; chrome APIs `beta` (tip `v0.54.0`, tag/PyPI deferred) | Package doctor, sim subset/parity, notebook handles, AppShell chrome — [Authoring loop](../api/AUTHORING_LOOP.md) · [What’s new in 0.54](whats-new-0.54.md) |

!!! note "Package train vs capability"

    Flagship packages are **Beta** maturity — pin `hedron>=0.54.0,<0.55`. The table above is
    **capability readiness** (Supported / Experimental / Deferred), not package maturity.

<details markdown>
<summary>Full Supported / Experimental / Deferred matrices</summary>

## Supported capabilities

| Capability | Package / surface | Status |
|---|---|---|
| Typed pages, fragments, built-ins | `hedron` + `hedron-core` | Supported |
| FastAPI routing, CSRF profiles, CLI, testing helpers | `hedron` | Supported |
| HTMX fragment loops, `InteractionResult` | `hedron` | Supported |
| `@app.refreshable` / `@app.command` / `refresh()` / `PatchSet` | `hedron` / `hedron-core` | Supported; API `beta`; compiles into the existing region / OOB stack |
| `ViewParams` / `FormBody` / `ActionHandle.form()` / `OutcomeMap` / class handlers | `hedron` / `hedron-core` | Supported; API `beta`; opt-in on 0.43 handles |
| `FeatureBundle` / `Hedron.include_feature` / `DataWorkspace` / `ChartInteraction` | `hedron-core` / `hedron` / `hedron-data` / `hedron-charts` | Supported; API `beta`; compiles onto 0.43–0.45 handles; not an executor |
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
| Component Explorer (dev) | `hedron[dev]` | Supported for local diagnostics; 0.50 pagination, provider isolation, catalog diffs, CLI/HTML/JSON agreement, and panels listed in [Explorer API](../api/EXPLORER.md) |
| Language-neutral conformance kit | `hedron[conformance]` | Supported |
| HDJ loop/macro budgets, a11y static checks | `hedron[jinja]` | Supported |
| AppScenario + HTMX InteractionResult asserts | `hedron.testing` | Supported |
| `region` / `@fragment` / `swap` ergonomics | `hedron` | Supported |
| Typed controls, surface chrome, Map, media Range | `hedron` / `hedron-core` | Supported |
| CameraCapture / MicrophoneCapture | `hedron` / `hedron-core` | Supported with permission/retention policy |
| BrowserContext/Storage, Math, IFrame | `hedron` / `hedron-core` | Supported |
| OIDC / session helpers + connection registry | `hedron` | Supported **helpers** (API `beta`); host auth/DI authoritative — **not** an IdP product |
| Curated extras toolkit (install-isolated) | `hedron[extras]` | Supported for the curated toolkit surface; **not** CodeEditor / TerminalView / joystick / device / sandbox. Experimental UI requires `hedron[experimental-ui]` plus `HEDRON_EXPERIMENTAL_UI` or explicit plugin enablement. Sandbox requires `hedron_extras_sandbox` / `HEDRON_EXTRAS_SANDBOX`. |
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
| Remote Gradio / HF Space client interop | `hedron[gradio]` / `hedron-gradio` | Supported for declared allowlisted destinations; pin `>=0.2.0,<0.3` |

Pin package versions in production. “Supported” does not mean a commercial SLA or
guaranteed multi-worker live-transport proof.

## Experimental (prefer documented fallbacks)

| Capability | Package / surface | Notes |
|---|---|---|
| Live interaction: SSE, streaming, WebSocket, preload | `hedron.experimental` (FastAPI) | Prefer [polling](live-interaction.md) |
| CodeEditor | `hedron[experimental-ui]` | **Host stub** (CSP-safe shell; no pinned CodeMirror 6 bundle); importable from `hedron_extras.experimental`, but omitted from default plugin registration |
| Browser-Python sandbox | opt-in `hedron_extras_sandbox` / `HEDRON_EXTRAS_SANDBOX` | Experimental; not registered by default `hedron[extras]`. Import stays `hedron_extras.sandbox` |
| TerminalView / joystick / device bridges | `hedron[experimental-ui]` | Fail-closed experimental surfaces; omitted from default plugin registration but not blocked from direct Python imports |
| Native desktop shell | docs recipe | Packaging guidance only |
| Flask / Django live helpers | adapters | Prefer polling |

## Tooling-grade Beta (not application production servers)

| Package | Role |
|---|---|
| `hedron[notebook]` / `hedron-notebook` | Localhost-oriented preview; tooling-grade Supported; not Supported production hosting |
| `hedron-sample-kit` | Installable reference plugin (`>=0.1.10,<0.2`) |
| `hedron-sim` | Deterministic offline fragment simulation (tooling-grade) |
| `packages/hedron-runtime-*` | Tooling-grade Java / Node conformance evaluators |

## Independent Beta satellites

| Package | Role |
|---|---|
| `hedron[mcp]` / `hedron-mcp` | Beta `0.2.1` (`>=0.2.0,<0.3`); deny-by-default Supported inventory; mutations Experimental |
| `hedron[gradio]` / `hedron-gradio` | Beta `0.2.0` (`>=0.2.0,<0.3`); allowlisted remote predict/stream/file transport |
| `hedron[charts]` / `hedron-charts` | Beta package (`>=0.2.0,<0.3`); first-party `ChartSpec` / `hedron-chart` and Matplotlib/static Supported; Plotly/Altair Experimental |
| `hedron[native]` / `hedron-native` | Optional Rust HTML-escape accel; pure-Python fallback Supported |

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

Phase-stamped folders (`data-app-0.15`, `dashboard-0.17`, …) are
**maintainer evidence stubs**, not product tutorials. The
[model-demo example](https://github.com/eddiethedean/hedron/tree/main/examples/model-demo-0.18)
is a runnable classifier. Live interaction sample:
[`examples/live-interaction`](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction)
(polling Supported; SSE/WS experimental).

## Recommended install

=== "uv (recommended)"

    ```bash
    uvx --from "hedron>=0.54.0,<0.55" hedron new my-app
    cd my-app && uv sync
    uv run uvicorn app:app --reload
    ```

=== "pip"

    ```bash
    pip install "hedron>=0.54.0,<0.55" "uvicorn[standard]"
    python -m hedron new my-app
    cd my-app && pip install -e .
    uvicorn app:app --reload
    ```

Pin `hedron>=0.54.0,<0.55`. Public-index notes: [Installation](../getting-started/installation.md).

Extras: `"hedron[data]>=0.54.0,<0.55"`, `"hedron[extras]>=0.54.0,<0.55"`,
`"hedron[jinja]>=0.54.0,<0.55"`, `"hedron[dev]>=0.54.0,<0.55"`,
`"hedron[notebook]>=0.54.0,<0.55"` (tooling / localhost),
`"hedron[mcp]>=0.54.0,<0.55"` (Beta Supported inventory),
`"hedron[gradio]>=0.54.0,<0.55"` (Beta satellite; pin `hedron-gradio>=0.2.0,<0.3`),
`"hedron[charts]>=0.54.0,<0.55"`, `"hedron[maps]>=0.54.0,<0.55"`, `"hedron[workbench]>=0.54.0,<0.55"`,
`"hedron[posit]>=0.54.0,<0.55"`,
and `"hedron-sample-kit>=0.1.10,<0.2"`.

## Role-specific wrappers

| Audience | Page |
|---|---|
| Quick fit check | [Evaluate Hedron](evaluate.md) |
| Ops ship checklist | [Ship a Hedron app](ship.md) · [Deployment](deployment.md) |
| Trust / maturity program | [Ship a Hedron app](ship.md) · [Evaluate Hedron](evaluate.md) |
| Security / procurement | [Enterprise diligence](enterprise-diligence.md) |

Also: [Upgrade](upgrade.md) · [What’s next](whats-next.md) · [Live interaction](live-interaction.md)
