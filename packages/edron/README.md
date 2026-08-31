<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/eddiethedean/hedron/v1.0/docs/assets/edron-logo-dark.svg">
    <img src="https://raw.githubusercontent.com/eddiethedean/hedron/v1.0/docs/assets/edron-logo-light.svg" width="460" alt="Edron">
  </picture>
</p>

<p align="center"><strong>Production-minded Python apps with a small, class-oriented API.</strong></p>

<p align="center">
  Dashboards · Internal tools · CRUD · Data workflows · No separate frontend
</p>

[![PyPI](https://img.shields.io/pypi/v/edron.svg)](https://pypi.org/project/edron/)
[![Python](https://img.shields.io/pypi/pyversions/edron.svg)](https://pypi.org/project/edron/)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=v1.0&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![Docs](https://readthedocs.org/projects/hedron/badge/?version=latest)](https://hedron.readthedocs.io/en/latest/guides/edron-user-guide/)
[![API: Stable](https://img.shields.io/badge/API-stable-brightgreen.svg)](https://hedron.readthedocs.io/en/latest/api/EDRON_REFERENCE/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/v1.0/packages/edron/LICENSE)

[Quickstart](https://hedron.readthedocs.io/en/latest/getting-started/edron-quickstart/) ·
[Showcase](https://hedron.readthedocs.io/en/latest/examples/edron-showcase/) ·
[User guide](https://hedron.readthedocs.io/en/latest/guides/edron-user-guide/) ·
[API by task](https://hedron.readthedocs.io/en/latest/api/EDRON_REFERENCE/) ·
[Deployment](https://hedron.readthedocs.io/en/latest/guides/edron-deployment/)

Edron is the batteries-included authoring layer for Hedron. You write pages, fragments, actions,
forms, data views, and workflows with ordinary Python classes. Edron lowers them into one
FastAPI-native application that renders accessible HTML on the server and progressively enhances
requests with HTMX.

There is no generated frontend project, Node.js build, callback graph, whole-script rerun model,
second router, or second state store. Built-in styling provides responsive layouts and coordinated
light/dark modes without requiring application CSS.

[![Edron Showcase operations workspace in dark mode](https://raw.githubusercontent.com/eddiethedean/hedron/v1.0/docs/assets/edron-showcase.jpg)](https://hedron.readthedocs.io/en/latest/examples/edron-showcase/)

<p align="center"><strong><a href="https://hedron.readthedocs.io/en/latest/examples/edron-showcase/">Explore the interactive showcase →</a> · <a href="https://github.com/eddiethedean/hedron/blob/v1.0/examples/edron-showcase/app.py">View the Edron-only source</a></strong></p>

> **Package maturity:** Stable · **Version documented:** `1.0.1`
>
> Every command and example below targets the Edron 1.0 API. Supported Python versions are
> 3.10–3.14; applications should retain the `<1.1` upper bound shown below.

## Start in under a minute

Create a project with [`uv`](https://docs.astral.sh/uv/):

```bash
uvx --from "edron>=1.0.1,<1.1" edron new my-app --template dashboard
cd my-app
uv sync
uv run edron run app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). The scaffold is ordinary Python with a
responsive application shell, built-in theme, page routes, and production-oriented configuration.

Adding Edron to an existing project is just as direct:

```bash
uv add "edron>=1.0.1,<1.1"
# or: python -m pip install "edron>=1.0.1,<1.1"
```

## Your first page

Create `app.py`:

```python
import edron as ed

app = ed.App(title="Sales", security="standard")


@app.page("/", title="Sales dashboard")
class Home(ed.Page):
    def render(self) -> None:
        self.heading("Sales dashboard")
        self.metric("Orders", 128, delta="+12")
        self.text("Useful HTML from a small, explicit Python application.")
```

Run it with either command:

```bash
edron run app:app --reload
# or: uvicorn app:app --reload
```

The `app` object is a normal ASGI application. Your existing server, reverse proxy, observability,
and deployment stack remain usable.

## The programming model

Edron has four primary ideas:

| Idea | Responsibility |
|---|---|
| `App` | Own routes, resources, packages, diagnostics, and deployment facts |
| `Page` | Build one request-local component tree through concise methods |
| `@fragment` | Define an independently addressable, refreshable read surface |
| `@action` | Process an unsafe request and return a bounded outcome |

Page instances are request-local controllers, never session state. Durable data belongs in
databases and services; authenticated principals and request facts belong in explicit
dependencies; application resources belong on `App`.

### Partial-page interaction

```python
from datetime import datetime, timezone

import edron as ed

app = ed.App(title="Operations", security="standard")


@app.page("/", title="Operations")
class Operations(ed.Page):
    def render(self) -> None:
        self.status()
        self.button("Refresh status", action=self.refresh_status)

    @ed.fragment
    def status(self) -> None:
        stamp = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
        self.text(f"All systems operational · {stamp}")

    @ed.action
    def refresh_status(self) -> ed.Outcome:
        return ed.refresh(self.status)
```

The initial request renders a complete page. The button sends a declared action request and only
the `status` fragment is replaced. Edron preserves CSRF policy, target allowlists, escaping, and
ordinary HTTP fallbacks through the entire flow.

### Layout with normal Python

```python
@app.page("/customers", title="Customers")
class Customers(ed.Page):
    def render(self) -> None:
        left, right = self.columns(2)

        left.heading("Customers", level=2)
        left.text("Request-local containers compose like any other Python value.")

        right.metric("Active", 412, delta="+18")
        right.metric("At risk", 7, delta="-2")
```

The built-in layout recipes collapse cleanly for narrow screens. Theme tokens coordinate light
and dark modes across forms, data, charts, maps, navigation, and status surfaces.

## A focused application vocabulary

Common page methods include:

```text
heading        text            markdown        code
metric         table           card            container
layout         columns         tabs            expander
text_input     number_input    selectbox       multiselect
slider         checkbox        date_input      form
button         download_button chart           map
image          audio           video
```

The stable root API is deliberately small. Package internals, private native objects, and
experimental adapters are outside the compatibility promise.

## What you get

| Concern | Built-in capability |
|---|---|
| Application structure | Class-oriented pages, fragments, actions, navigation targets, inheritance, and feature packages |
| UI and layout | Responsive shells, cards, columns, tabs, forms, dialogs, status, media, and light/dark themes |
| Data applications | `DataSource`, `DataWorkspace`, explicit columns, bounded queries, typed edit intents, and CSV export |
| Charts and maps | Stable first-party chart/map lowering with accessible fallbacks and bounded payloads |
| Services | Typed dependencies, lazy app/request resources, scoped caches, health metadata, and secret references |
| Long-running work | `JobFlow`, pluggable backends, bounded results, polling, cancellation, and status events |
| Delivery | Static source checks, application explanations, capability diagnostics, deployment profiles, manifests, and conformance reports |
| Migration | Review-first Streamlit analysis, generated project structure, source maps, and explicit TODOs |

Edron includes Hedron, data, chart, map, Markdown, sanitization, and Uvicorn foundations. Optional
extras install only the third-party libraries your application actually uses:

```bash
uv add "edron[pandas,plotly,sqlalchemy]>=1.0.1,<1.1"
```

Available extras are `pandas`, `polars`, `pyarrow`, `plotly`, `altair`, `matplotlib`, and
`sqlalchemy`.

## Data boundaries stay visible

Data editing is deny-by-default. Applications declare keys, columns, allowed query operations,
writable fields, validation, authorization, concurrency policy, and audit behavior instead of
shipping an unbounded object to the browser.

```python
import edron as ed

source = ed.DataSource.in_memory(
    [
        {"id": "1", "name": "Northwind", "status": "open"},
        {"id": "2", "name": "Contoso", "status": "closed"},
    ],
    key_field="id",
    columns=(
        ed.Column("id", read_only=True, sortable=True),
        ed.Column("name", sortable=True, filterable=True),
        ed.Column("status", sortable=True, filterable=True),
    ),
    sort_fields=("id", "name", "status"),
    filter_fields=("name", "status"),
)
```

`DataWorkspace` adds bounded paging, filtering, sorting, search, selection, export, and typed edit
intents. The application still owns row authorization, database sessions, transactions,
persistence, and durable audit records.

## Resources, caching, and jobs are explicit

Register lazy resources at the application boundary and expose secret names—not secret values—in
diagnostic metadata:

```python
import os

import edron as ed

app = ed.App(title="Orders", security="standard")


def open_database() -> object:
    return make_database(os.environ["DATABASE_URL"])


database = app.resource(
    "database",
    open_database,
    kind="sqlalchemy",
    secret_refs={"dsn": "DATABASE_URL"},
)


@app.page("/", title="Orders")
class Orders(ed.Page):
    db = database

    def render(self) -> None:
        self.metric("Open orders", count_open_orders(self.db))


@ed.cache_data(ttl=60, scope="tenant", vary_on=("tenant_id",))
def load_summary(tenant_id: str) -> dict[str, int]:
    return query_summary(tenant_id)
```

Use `JobFlow` when work must outlive a request. Configure shared cache and job backends before
running multiple workers; deployment diagnostics report process-local backends explicitly.

## Inspect before you ship

```bash
# Parse and check source without executing it
edron check app.py

# Inspect a trusted application's pages, fragments, and actions
edron explain app:app

# Diagnose capabilities and topology-specific deployment facts
edron doctor app:app --profile container
edron deploy-check --profile reverse-proxy --format json
```

`edron check --format sarif` emits CI-friendly findings. `app.manifest()` and
`app.conformance()` return deterministic, bounded reports for promotion and release gates.

## Moving from Streamlit

Edron offers familiar page, input, metric, data, and chart vocabulary without emulating
Streamlit's global rerun runtime or mutable session dictionary.

```bash
edron migrate streamlit streamlit_app.py --out migrated-app
```

Migration is static and review-first: source is not executed or overwritten. The output includes
a fresh project, deterministic findings, a source map, and explicit TODOs for behavior that needs
human judgment.

[Read the migration center](https://hedron.readthedocs.io/en/latest/guides/streamlit-migration/).

## One runtime, one authority

```text
Edron page / fragment / action / resource
                    |
                    v
      Hedron page / view / action / dependency
                    |
                    v
        FastAPI + server-rendered HTML + HTMX
```

Edron is an authoring facade, not a parallel web framework. It preserves Hedron's renderer,
request lifecycle, security policy, assets, and deployment model while presenting a smaller
application-facing API.

Choose [Hedron](https://pypi.org/project/hedron/) directly when you prefer explicit component
trees, FastAPI-native function routes, custom host integration, or framework extension points.

## Production checklist

Edron provides secure defaults and inspectable boundaries. Before deployment:

- Set a strong application-specific session secret and deliberate security profile.
- Authenticate and authorize in trusted dependencies and action boundaries.
- Use shared state, cache, and job backends for multi-worker deployments.
- Keep transactions, retries, idempotency, tenancy, and audit persistence in application services.
- Treat user, database, upload, and generated content as untrusted input.
- Validate proxy trust, root paths, HTTPS, cookies, artifacts, and health behavior against the
  actual deployment topology.
- Prefer polling for durable job status unless SSE/WebSocket buffering, timeouts, and backpressure
  have been verified.

Edron is not an ORM, identity provider, database, durable job broker, hosted platform, or browser
SPA runtime.

## See the complete application

The [Edron Showcase](https://hedron.readthedocs.io/en/latest/examples/edron-showcase/) is a
responsive, light/dark operations workspace with pages, layouts, fragments, actions, metrics,
tables, charts, tabs, and outcomes. The documentation links the same runnable source represented
by the simulation. Every application surface is authored through public Edron APIs, with no custom
application CSS or Hedron escape hatches.

## Learn more

- [Five-minute quickstart](https://hedron.readthedocs.io/en/latest/getting-started/edron-quickstart/)
- [Edron user guide](https://hedron.readthedocs.io/en/latest/guides/edron-user-guide/)
- [API by task](https://hedron.readthedocs.io/en/latest/api/EDRON_REFERENCE/)
- [Edron API](https://hedron.readthedocs.io/en/latest/api/EDRON/)
- [Example catalog](https://hedron.readthedocs.io/en/latest/examples/edron/)
- [Cookbook](https://hedron.readthedocs.io/en/latest/guides/cookbook/)
- [Deployment](https://hedron.readthedocs.io/en/latest/guides/edron-deployment/)
- [Source](https://github.com/eddiethedean/hedron/tree/v1.0/packages/edron)
- [Changelog](https://github.com/eddiethedean/hedron/blob/v1.0/packages/edron/CHANGELOG.md)
- [Issues](https://github.com/eddiethedean/hedron/issues)

## License

Edron is available under the [MIT License](https://github.com/eddiethedean/hedron/blob/v1.0/packages/edron/LICENSE).
