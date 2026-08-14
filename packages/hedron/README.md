# Hedron

[![PyPI](https://img.shields.io/pypi/v/hedron.svg)](https://pypi.org/project/hedron/)
[![Python](https://img.shields.io/pypi/pyversions/hedron.svg)](https://pypi.org/project/hedron/)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

**Build admin tools, CRUD apps, and dashboards in Python—without building a separate
frontend.**

Hedron is a typed, server-rendered UI framework for FastAPI. Routes return Python
components, Hedron renders safe HTML, and HTMX updates just the part of the page that
changed. You keep FastAPI's routing, dependency injection, middleware, and JSON APIs;
you do not need a Node.js toolchain or a full-script rerun model.

![A Hedron app with a status panel updated by HTMX](https://raw.githubusercontent.com/eddiethedean/hedron/main/docs/assets/hello-refresh.jpg)

## Try it in five minutes

Requires Python 3.11–3.14. The fastest path uses
[`uv`](https://docs.astral.sh/uv/getting-started/installation/):

```bash
uvx --from "hedron>=0.39.0,<0.40" hedron new my-hedron-app
cd my-hedron-app
uv sync
uv run uvicorn app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000), then click **Refresh status**.
Only the status region is returned and swapped into the page.

The generated app is ordinary Python:

```python
import os
from datetime import UTC, datetime

from hedron import Hedron, Page, RefreshButton, Stack, Text, html, swap

app = Hedron(
    title="Hedron App",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "replace-in-production"),
)

status = app.region("service-status", description="Live status panel")


def status_panel():
    stamp = datetime.now(UTC).strftime("%H:%M:%S UTC")
    return html.div(
        Text(f"All systems operational · refreshed {stamp}"),
        id=status.id,
        role="status",
        aria={"live": "polite"},
    )


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            Text("Hello from Hedron"),
            status_panel(),
            RefreshButton.for_region(status, href="/status", label="Refresh status"),
        ),
        title="Home",
    )


@app.fragment("/status", region=status)
def refresh_status():
    return swap(status_panel())
```

The declared `region` is both the browser swap target and a server-side allowlist.
Requests aimed at undeclared targets fail closed.

[Follow the first-app walkthrough](https://hedron.readthedocs.io/en/latest/getting-started/quickstart/)
or browse the
[single-file examples](https://hedron.readthedocs.io/en/latest/examples/single-file/).

## What Hedron gives you

| Need | Hedron provides |
|---|---|
| Server-rendered UI | Typed pages, layouts, forms, tables, dialogs, status views, and media components |
| Partial-page interaction | Declared HTMX fragments, out-of-band updates, progressive-enhancement paths, and target allowlists |
| FastAPI integration | Normal routes, dependencies, middleware, lifespan hooks, responses, and OpenAPI alongside UI routes |
| Safer defaults | Contextual escaping, typed URL/HTML trust boundaries, CSRF profiles, and conservative caching |
| Production building blocks | Polling jobs, diagnostics, testing helpers, build manifests, deployment guidance, and Flask/Django adapters |

Your application still owns authentication, authorization, persistence, tenancy, and
deployment. Hedron is not an ORM, identity provider, hosted service, or client-side SPA
runtime.

## When it fits

Choose Hedron when you want to build forms, internal tools, admin surfaces, or dashboards
as a conventional web application while keeping most UI code in typed Python. It is
especially useful when raw FastAPI plus Jinja plus HTMX would leave you assembling the
same rendering, fragment, CSRF, asset, and component conventions yourself.

Choose Streamlit for notebook-style, full-script-rerun data apps. Choose raw FastAPI and
templates when you do not want a component framework. Choose a client-side framework when
the product genuinely needs a large browser-side state model.

Coming from Streamlit? Start with the
[migration center](https://hedron.readthedocs.io/en/latest/guides/streamlit-migration/).

## Install

Pin the current Beta train so upgrades are intentional:

```bash
uv add "hedron>=0.39.0,<0.40" "uvicorn[standard]"
# or
python -m pip install "hedron>=0.39.0,<0.40" "uvicorn[standard]"
```

**Package maturity:** Beta · **Train:** `0.38.x` · last published `0.39.0` ·
pin `>=0.39.0,<0.40`

Before deploying, read
[What's ready today](https://hedron.readthedocs.io/en/latest/guides/whats-ready/) and the
[shipping guide](https://hedron.readthedocs.io/en/latest/guides/ship/). Polling is the
supported production status-update path; SSE and WebSocket helpers remain experimental.

## Add only what you need

The base package includes the FastAPI application, typed UI, HTML renderer, HTMX
interactions, security profiles, and CLI. Integrations are optional:

| Install | Adds |
|---|---|
| `hedron[data]` | DataTable and DataEditor |
| `hedron[charts]` | Charts with a compatible satellite floor |
| `hedron[jinja]` | Optional `.hdj` templates |
| `hedron[dev]` | Component Explorer |
| `hedron[extras]` | Curated workbenches |
| `hedron[auth]` | Authlib OIDC helpers |
| `hedron[markdown]` | Markdown rendering and sanitization |
| `hedron[native]` | Optional Beta native acceleration |
| `hedron[mcp]` | Beta MCP projection (Supported inventory; mutations Experimental) |
| `hedron[notebook]` | Beta tooling-grade localhost preview; not a production server |
| `hedron[gradio]` | Beta allowlisted Gradio/Hugging Face client interoperability |
| `hedron[elements]` | Alpha Web Component ABI incubator |

For example:

```bash
uv add "hedron[data,dev]>=0.39.0,<0.40"
```

Charts require the fixed compatible floor:

```bash
uv add "hedron[charts]>=0.39.0,<0.40"
```

See the full
[installation and extras guide](https://hedron.readthedocs.io/en/latest/getting-started/installation/)
and the
[compatibility matrix](https://hedron.readthedocs.io/en/latest/COMPATIBILITY/).

## Already have a FastAPI app?

You can mount Hedron's router and static assets without replacing your application:

```python
from fastapi import FastAPI
from hedron import HTML, HedronRouter, Text, hedron_response, mount_hedron_static
from hedron.security.policy import SecurityPolicy

app = FastAPI()
app.state.hedron_security = SecurityPolicy.from_name("standard")
mount_hedron_static(app)

ui = HedronRouter()


@ui.get("/hello", **hedron_response())
def hello():
    return HTML(Text("Hello from Hedron"))


app.include_router(ui)
```

[Read the existing-FastAPI guide](https://hedron.readthedocs.io/en/latest/guides/plain-fastapi/).
Flask and Django hosts are available through
[`hedron-flask`](https://pypi.org/project/hedron-flask/) and
[`hedron-django`](https://pypi.org/project/hedron-django/); both share the framework-neutral
[`hedron-core`](https://pypi.org/project/hedron-core/) renderer.

## CLI

```bash
python -m hedron new demoapp
python -m hedron --app app:app routes
python -m hedron --app app:app components
python -m hedron --app app:app preview home
python -m hedron --app app:app check
python -m hedron --app app:app graph
```

## Learn more

- [Documentation](https://hedron.readthedocs.io/en/latest/)
- [Learning path](https://hedron.readthedocs.io/en/latest/getting-started/learning-path/)
- [Architecture](https://hedron.readthedocs.io/en/latest/ARCHITECTURE/)
- [Components](https://hedron.readthedocs.io/en/latest/components/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron)
- [Issues](https://github.com/eddiethedean/hedron/issues)

## License

MIT. See the [license](https://github.com/eddiethedean/hedron/blob/main/LICENSE).
