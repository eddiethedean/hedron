# What’s ready today

**Ship today (pinned CRUD / admin on FastAPI, Flask, or Django):** pages, HTMX
fragments, CSRF, polling job status, DataTable, first-party charts.
**Do not treat as production defaults:** SSE, WebSocket, Plotly/Altair, human
screen-reader claims. The coordinated 1.0 packages are **Stable** for the enumerated stable
inventory; independent satellites retain their own Beta/tooling labels. There is no SLA.

This page is the **adopter** maturity summary for the published **1.0.x** train
([Current release and support](current-release.md)). Full capability matrices and
maintainer gate notes:
[What’s ready — evidence](whats-ready-evidence.md).

!!! tip "Can I ship an internal admin app?"

    **Yes, with pins.** Walkthrough:
    [Build your first app](../getting-started/quickstart.md) →
    [Minimal form](minimal-form.md) →
    [What is HTMX?](../getting-started/what-is-htmx.md). Ship checklist:
    [Ship a Hedron app](ship.md).

## Labels in one screen

| Label | Meaning |
|---|---|
| **Supported** | Works on the current train when pinned — **≠** API `stable` and **≠** package Beta |
| **Experimental** | Public; may change; prefer documented fallbacks (usually polling) |
| **Deferred** | Documented, not ready — do not treat as Supported |

Edron and Hedron **1.0.0** are published; the **0.67.0** train is the migration baseline.
Package maturity, capability
readiness, and API compatibility are separate axes —
[Maturity labels](../getting-started/how-to-read.md).

The two foundational runtime distributions, `hedron-core` and `hedron`, are checked in
Pyright strict mode with zero warnings. Commit and release CI use a warning-fatal package gate,
so new type diagnostics cannot accumulate behind an otherwise green build.

Human accessibility testing protocol engineering is on the train; **compensated
screen-reader sessions are not Supported yet**.

!!! warning "Live transports"

    SSE, focused streaming, WebSocket channels, and navigation preload are
    **experimental** (`hedron.experimental`). Prefer [polling](live-interaction.md) in
    production.

## Ship today vs not defaults

| Job | Status | Start here |
|---|---|---|
| CRUD / admin / forms | **Supported** | [First app](../getting-started/quickstart.md) |
| Pages (`@app.page`) | **Supported** | [Quickstart](../getting-started/quickstart.md) |
| HTMX views / actions (`@app.view` / `@app.action`) | **Supported** | [Which interaction API?](../getting-started/interaction-apis.md) |
| Multi-worker durable jobs (polling) | **Supported** with shared Redis | [Jobs](../api/JOBS.md) |
| DataTable / DataEditor | **Supported** (`hedron[data]`) | [Data apps](data-apps.md) |
| Charts (first-party / Matplotlib) | **Supported**; Plotly/Altair **Experimental** | [Chart API](../api/CHART.md) |
| Flask / Django hosts | **Supported** (host CSRF/pages; not FastAPI facade parity) | [Flask](../getting-started/flask.md) · [Django](../getting-started/django.md) |
| Live SSE / WebSocket | **Experimental** | Prefer [polling](live-interaction.md) |
| Human screen-reader AT | **Not Supported** yet | Protocol engineering only — [evidence](whats-ready-evidence.md) |

### Host capability cheat sheet

| Capability | FastAPI (`hedron`) | Flask (`hedron-flask`) | Django (`hedron-django`) |
|---|---|---|---|
| Pages + HTMX fragments + CSRF | Supported | Supported | Supported |
| `@app.page` / `@app.action` facades | Supported | Not on this host | Not on this host |
| Polling job status | Supported | Supported | Supported |
| Live SSE / WebSocket helpers | Experimental | Prefer polling | Prefer polling |
| DataTable / charts extras | Supported with pins | Supported with pins | Supported with pins |

Need the long inventory (MCP, Gradio, Workbench, Application DX, Deferred rows)?
Use [What’s ready — evidence](whats-ready-evidence.md).

## Recommended install

=== "uv (recommended)"

    ```bash
    uvx --from "hedron>=1.0.0,<1.1" hedron new my-app
    cd my-app && uv sync
    uv run uvicorn app:app --reload
    ```

=== "pip"

    ```bash
    pip install "hedron>=1.0.0,<1.1" "uvicorn[standard]"
    python -m hedron new my-app
    cd my-app && pip install -e .
    uvicorn app:app --reload
    ```

Pin the stable release: `hedron>=1.0.0,<1.1`. Extras and compatibility notes:
[Installation](../getting-started/installation.md). Sample kit:
`hedron-sample-kit>=0.2.3,<0.3`.

## Next

| Audience | Page |
|---|---|
| Quick fit check | [Evaluate Hedron](evaluate.md) |
| Ops ship checklist | [Ship a Hedron app](ship.md) · [Deployment](deployment.md) |
| Security / procurement | [Enterprise diligence](enterprise-diligence.md) · [Threat model](threat-model.md) |
| Full matrices | [What’s ready — evidence](whats-ready-evidence.md) |
| Upgrade / roadmap | [Upgrade](upgrade.md) · [What’s next](whats-next.md) |
