# Hedron

[![PyPI](https://img.shields.io/pypi/v/hedron.svg)](https://pypi.org/project/hedron/)
[![Python](https://img.shields.io/pypi/pyversions/hedron.svg)](https://pypi.org/project/hedron/)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![Docs](https://readthedocs.org/projects/hedron/badge/?version=latest)](https://hedron.readthedocs.io/en/latest/)
[![Pyright: strict](https://img.shields.io/badge/Pyright-strict-3178c6.svg)](https://microsoft.github.io/pyright/)
[![Status: Stable](https://img.shields.io/badge/status-stable-brightgreen.svg)](https://pypi.org/project/hedron/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

**Build FastAPI-native admin tools, CRUD applications, forms, and dashboards with Python
components and server-rendered HTML.**

Hedron combines FastAPI, a typed component model, and HTMX-style partial-page interaction. Routes
return Python component trees; Hedron renders safe HTML documents or fragments. Your ordinary
FastAPI routes, dependencies, middleware, lifespan hooks, JSON endpoints, and OpenAPI remain
available beside the UI.

There is no generated frontend project, Node.js build, virtual DOM, or full-script rerun loop.

**Package maturity:** Stable · **Release:** `1.0.x` · **Python:** 3.10–3.14 ·
**Typing:** Pyright strict, zero warnings

The warning-free typing baseline is enforced in commit and release CI with
`pyright --warnings`; a new strict-mode diagnostic fails the build rather than becoming
untracked typing debt.

> Looking for the shortest application-authoring path? [Edron](https://pypi.org/project/edron/)
> adds class-oriented pages, a compact dashboard vocabulary, batteries-included data/chart/map
> dependencies, and Streamlit migration tooling on top of this exact Hedron runtime.

## Quickstart

The fastest path uses [`uv`](https://docs.astral.sh/uv/):

```bash
uvx --from "hedron>=1.0.0,<1.1" hedron new my-hedron-app
cd my-hedron-app
uv sync
uv run hedron run app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). The generated project is ordinary Python and
demonstrates the canonical page, view, and action roles with progressive form fallbacks.

![A Hedron application with a status panel refreshed in place](https://raw.githubusercontent.com/eddiethedean/hedron/main/docs/assets/hello-refresh.jpg)

Install Hedron directly when adding it to an existing project:

```bash
uv add "hedron>=1.0.0,<1.1" "uvicorn[standard]"
# or: python -m pip install "hedron>=1.0.0,<1.1" "uvicorn[standard]"
```

## A small, explicit core

The canonical 1.0 function roles are `page`, `view`, and `action`:

| Role | HTTP responsibility | Typical return value |
|---|---|---|
| `@app.page` | Render a complete navigable page | A component tree or explicit `Page` |
| `@app.view` | Render an independently addressable read fragment | A component or fragment tree |
| `@app.action` | Process an unsafe request and declare its result | An outcome such as `refresh(...)` |

Here is the central page/view model in one file:

```python
import os
from datetime import datetime, timezone

from hedron import Hedron, Stack, Text, html

app = Hedron(
    title="Operations",
    security="standard",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "replace-in-production"),
)


@app.view("/status")
def status():
    stamp = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    return html.div(
        Text(f"All systems operational · {stamp}"),
        role="status",
        aria={"live": "polite"},
    )


@app.page("/")
def home():
    return Stack(
        Text("Operations"),
        status(),
        status.refresh_button("Refresh status"),
    )
```

Run it with `hedron run app:app --reload` or `uvicorn app:app --reload`.

The `status` handle is both composable and addressable: calling it inside `home()` places its
initial output in the page, while `status.path` gives the browser a declared endpoint for later
refreshes. Hedron validates fragment targets against the route's policy and fails closed when a
request tries to update an undeclared target.

Actions add a typed unsafe-request boundary:

```python
from typing import Annotated

from pydantic import BaseModel, Field

from hedron import FormBody, Text


class Note(BaseModel):
    message: str = Field(min_length=1, max_length=200)


@app.action("/notes", fallback="/")
def add_note(note: Annotated[Note, FormBody()]):
    save_authorized_note(note)
    return Text("Note saved")


# In a page component tree:
# add_note.form(submit_label="Save note")
```

Validation happens at the typed action boundary. Authentication, row-level authorization,
transactions, idempotency, and audit persistence remain application responsibilities.

## Why Hedron

| Need | Hedron provides |
|---|---|
| Server-rendered UI | Typed components for pages, layouts, forms, tables, dialogs, navigation, status, and media |
| Partial-page interaction | Addressable views, declared targets, HTMX swaps, out-of-band updates, actions, and progressive fallbacks |
| FastAPI integration | Standard dependencies, middleware, lifespan, responses, mounts, JSON routes, and OpenAPI alongside UI routes |
| Safer defaults | Contextual escaping, safe URL types, explicit trusted-HTML boundaries, CSRF profiles, security headers, and conservative caching |
| Production building blocks | Typed forms, polling jobs, build manifests, diagnostics, test generation, conformance reports, and observability hooks |
| Extension | Feature bundles, package workflows, Jinja/HDJ, Web Components, charts, maps, adapters, and a framework-neutral renderer |

Hedron is especially useful when raw FastAPI + Jinja + HTMX would leave your team rebuilding the
same component, fragment, target, CSRF, asset, accessibility, and diagnostic conventions.

Choose another tool when its execution model is a better fit:

- Choose **Edron** for higher-level, class-oriented application authoring.
- Choose **Streamlit** for notebook-style exploration built around full-script reruns.
- Choose **plain FastAPI and templates** when you do not want a component framework.
- Choose a **client-side framework** when the product genuinely needs a large browser-owned state
  model or offline-first client runtime.

## Components are ordinary Python values

Components compose into explicit trees and render with contextual escaping:

```python
from hedron import Card, Heading, SafeUrl, Stack, Text, UrlPurpose, html

summary = Card(
    Stack(
        Heading("Quarterly summary", level=2),
        Text("Revenue increased 18%."),
        html.a(
            "View report",
            href=SafeUrl.parse("/reports/q4", purpose=UrlPurpose.NAVIGATION),
        ),
    )
)
```

Hedron includes application shells, navigation, grids, cards, fields, forms, alerts, dialogs,
tables, pagination, uploads, media, progress/status components, accessibility primitives, and a
typed HTML builder. Project-owned components are normal Python packages and can participate in the
same theme, asset, accessibility, and inspection contracts.

User-controlled strings remain text. Raw HTML and URLs cross explicit trust boundaries; use safe
URL types and sanitization instead of passing database, tenant, upload, or prompt content as
trusted markup.

## Add only what you need

The base package includes the FastAPI application, component API, renderer integration,
interaction primitives, security profiles, state foundations, and CLI. Extras install coordinated
satellite packages or optional integrations:

| Install | Adds |
|---|---|
| `hedron[data]` | DataTable, DataEditor, and data workspace foundations |
| `hedron[charts]` | First-party chart components and adapters |
| `hedron[maps]` | Accessible map components and layer policies |
| `hedron[jinja]` | Optional `.hdj` component templates |
| `hedron[dev]` | Component Explorer |
| `hedron[markdown]` | Markdown rendering and sanitization |
| `hedron[auth]` | Authlib OIDC integration helpers |
| `hedron[extras]` | Curated higher-level workbenches |
| `hedron[native]` | Optional native acceleration |
| `hedron[elements]` | Web Component authoring and ABI support |
| `hedron[conformance]` | Published language-neutral conformance tooling |
| `hedron[notebook]` | Localhost notebook preview tooling |
| `hedron[gradio]` | Allowlisted Gradio/Hugging Face client interop |
| `hedron[mcp]` | MCP projection and capability inventory |
| `hedron[posit]` | Posit Workbench and Connect lifecycle integration |

For example:

```bash
uv add "hedron[data,charts,dev]>=1.0.0,<1.1"
```

Satellite packages may have independent versions. Use the
[compatibility matrix](https://hedron.readthedocs.io/en/latest/COMPATIBILITY/) instead of guessing
compatible floors.

## Bring Hedron to an existing FastAPI app

You can mount Hedron routes and static assets without replacing application construction:

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

Read [Add Hedron to an existing FastAPI application](https://hedron.readthedocs.io/en/latest/guides/plain-fastapi/)
for lifespan, security, assets, root paths, and response behavior.

Hedron's renderer is framework-neutral. First-party adapters provide Flask and Django hosts:

```bash
uv add "hedron-flask>=1.0.0,<1.1"
# or: uv add "hedron-django>=1.0.0,<1.1"
```

## Security and ownership boundaries

Hedron supplies tools and safer defaults, but your application remains the authority for domain
and platform decisions:

- Configure a production session secret; never ship the scaffold fallback.
- Authenticate users and authorize every protected page, view, action, row, and download.
- Keep database transactions, tenancy, persistence, and durable audit records in application
  services.
- Use shared cache, state, and job backends when running multiple workers.
- Treat all user, database, upload, and generated content as untrusted input.
- Prefer polling for production job status unless proxy buffering, timeouts, and backpressure are
  verified for SSE or WebSockets.
- Run security and deployment checks against the topology you will actually operate.

Hedron is not an ORM, identity provider, database, job broker, hosted service, or client-side SPA
runtime. Start with the [security guide](https://hedron.readthedocs.io/en/latest/guides/security/),
[threat model](https://hedron.readthedocs.io/en/latest/guides/threat-model/), and
[deployment guide](https://hedron.readthedocs.io/en/latest/guides/deployment/).

## CLI workflow

Hedron's CLI is designed to make application structure and release facts inspectable:

```bash
# Create teaching projects
hedron new demo --template minimal
hedron new admin --template crud
hedron new metrics --template dashboard
hedron new worker-ui --template task

# Inspect a trusted application
hedron --app app:app routes
hedron --app app:app components
hedron --app app:app graph

# Run diagnostics and static 1.0 migration checks
hedron --app app:app check
hedron check --project . --target 1.0 --format sarif

# Build registered assets and inspect the installed package fleet
hedron --app app:app build
hedron fleet
```

Other commands cover component previews, accessibility inspection/ejection, security posture,
themes and styles, generated interaction tests, conformance, package authoring, native
acceleration, framework migrations, and offline upgrade reports. Run `hedron --help` or read the
[CLI reference](https://hedron.readthedocs.io/en/latest/api/CLI/).

## Learn more

- [Choose Edron or Hedron](https://hedron.readthedocs.io/en/latest/getting-started/choose-layer/)
- [Documentation](https://hedron.readthedocs.io/en/latest/)
- [Installation](https://hedron.readthedocs.io/en/latest/getting-started/installation/)
- [First application](https://hedron.readthedocs.io/en/latest/getting-started/quickstart/)
- [Core concepts](https://hedron.readthedocs.io/en/latest/getting-started/core-concepts/)
- [Learning path](https://hedron.readthedocs.io/en/latest/getting-started/learning-path/)
- [Hedron API](https://hedron.readthedocs.io/en/latest/api/HEDRON/)
- [Cookbook](https://hedron.readthedocs.io/en/latest/guides/cookbook/)
- [Testing](https://hedron.readthedocs.io/en/latest/guides/testing/)
- [Architecture](https://hedron.readthedocs.io/en/latest/ARCHITECTURE/)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron/CHANGELOG.md)
- [Issues](https://github.com/eddiethedean/hedron/issues)

## License

Hedron is available under the [MIT License](https://github.com/eddiethedean/hedron/blob/main/LICENSE).
