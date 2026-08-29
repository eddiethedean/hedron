# Edron

[![PyPI](https://img.shields.io/pypi/v/edron.svg)](https://pypi.org/project/edron/)
[![Python](https://img.shields.io/pypi/pyversions/edron.svg)](https://pypi.org/project/edron/)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![Docs](https://readthedocs.org/projects/hedron/badge/?version=latest)](https://hedron.readthedocs.io/en/latest/guides/edron-user-guide/)
[![Status: Stable](https://img.shields.io/badge/status-stable-brightgreen.svg)](https://pypi.org/project/edron/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/packages/edron/LICENSE)

**Build dashboards, internal tools, CRUD applications, and data workflows in Python—with a
small API and no separate frontend project.**

Edron is the batteries-included, class-oriented authoring layer for Hedron. You write ordinary
Python pages, fragments, and actions; Edron lowers them into one FastAPI-native Hedron application
that renders accessible HTML and adds partial-page interaction through HTMX.

- No Node.js toolchain or generated frontend application
- No whole-script rerun model or callback graph
- No second router, renderer, state store, or security authority
- Full access to the native Hedron application when you need it

**Package maturity:** Stable · **Release:** `1.0.x` · **Python:** 3.10–3.14

Pin the minor train in applications and upgrade deliberately after reading the release notes.

## Quickstart

Create a project with [`uv`](https://docs.astral.sh/uv/):

```bash
uvx --from "edron>=1.0.0,<1.1" edron new my-app --template minimal
cd my-app
uv sync
uv run edron run app:app --reload
```

Or install Edron into an existing project:

```bash
uv add "edron>=1.0.0,<1.1"
# or: python -m pip install "edron>=1.0.0,<1.1"
```

Create `app.py`:

```python
import edron as ed

app = ed.App(title="Sales", security="standard")


@app.page("/", title="Sales dashboard")
class Home(ed.Page):
    def render(self) -> None:
        self.metric("Orders", 128, delta="+12")
        self.text("Useful HTML from a small, explicit Python application.")
```

Run it and open [http://127.0.0.1:8000](http://127.0.0.1:8000):

```bash
edron run app:app --reload
```

The `app` object is a normal ASGI application. You can launch it with Edron's convenience command,
Uvicorn, or your existing ASGI deployment stack.

## Interactive showcase

Explore the [interactive Edron Showcase](https://hedron.readthedocs.io/en/latest/examples/edron-showcase/).
Its runnable source uses only `edron`; the demo covers pages, layouts, fragments, actions, charts,
tables, tabs, and outcomes without Hedron escape hatches.

## The programming model

An Edron application has four primary ideas:

| Idea | Role |
|---|---|
| `App` | Owns the native application, routes, resources, packages, diagnostics, and deployment facts |
| `Page` | A fresh request-local controller whose methods append server-rendered components |
| `@fragment` | An independently addressable, refreshable read surface |
| `@action` | An explicit unsafe-request command that returns a bounded outcome |

Page instances are never session state. Put database sessions, authenticated principals, durable
state, and services in explicit dependencies or app-owned resources.

### Add a partial-page interaction

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

The initial request renders a complete page. The button sends a declared action request, and the
result refreshes only the `status` fragment. Edron preserves Hedron's CSRF policy, target
allowlists, escaping, and ordinary HTTP boundaries throughout the flow.

### Compose without a template language

```python
@app.page("/customers", title="Customers")
class Customers(ed.Page):
    def render(self) -> None:
        left, right = self.columns(2)

        left.heading("Customers", level=2)
        left.text("Compose request-local containers with normal Python.")

        right.metric("Active", 412, delta="+18")
        right.metric("At risk", 7, delta="-2")
```

Common page methods include `heading`, `text`, `markdown`, `code`, `metric`, `table`, `card`,
`container`, `layout`, `columns`, `tabs`, `expander`, `text_input`, `number_input`, `selectbox`,
`multiselect`, `slider`, `checkbox`, `date_input`, `form`, `button`, `download_button`, `chart`,
`map`, `image`, `audio`, and `video`.

## Built for application work

Edron keeps high-level ergonomics and production boundaries in the same model.

| Need | Edron provides |
|---|---|
| Pages and reusable UI | `Page`, `@app.page`, `fragment`, `action`, `inherit`, and `expose` |
| Layout and navigation | Bounded layout recipes, columns, tabs, navigation targets, and feature packages |
| Forms and interactions | Typed inputs, Pydantic forms, bound actions, confirmations, refreshes, and success outcomes |
| Data applications | `DataSource`, `DataWorkspace`, explicit columns, bounded query policy, typed edit intents, and CSV export |
| Charts, maps, and media | First-party chart/map lowering plus image, audio, video, and download helpers |
| Services and performance | Typed dependencies, lazy resources, scoped caches, health metadata, and secret references |
| Long-running work | `JobFlow`, pluggable backends, bounded results, polling, and status events |
| Reuse and extension | Feature packages, capability promotion, native component inclusion, and deterministic manifests |
| Delivery | Source checks, application explanations, capability diagnostics, deployment profiles, and conformance reports |

Edron includes the Hedron, data, chart, map, Markdown, sanitization, and Uvicorn foundations needed
by its standard API. Optional extras activate third-party data and plotting integrations:

```bash
uv add "edron[pandas,plotly,sqlalchemy]>=1.0.0,<1.1"
```

Available extras are `pandas`, `polars`, `pyarrow`, `plotly`, `altair`, `matplotlib`, and
`sqlalchemy`. Install only the libraries your application uses.

## Data boundaries stay visible

Data editing is deny-by-default. Applications declare keys, columns, query capabilities, writable
fields, validation, authorization, concurrency policy, and audit behavior rather than handing an
unbounded object to the browser.

```python
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
intents. Your application still owns row authorization, database sessions, transactions,
persistence, and durable audit records.

## Resources, caching, and jobs are explicit

Register lazy application resources at the application boundary and refer to secret names—not
secret values—in diagnostic metadata:

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

Use `JobFlow` when work must outlive a request. Select a shared backend before using multiple
workers; process-local state and jobs are intentionally reported by the deployment diagnostics.

## Tooling you can run before production

```bash
# Parse and check source without executing it
edron check app.py

# Inspect the trusted app's registered pages, fragments, and actions
edron explain app:app

# Diagnose required/optional capabilities and deployment facts
edron doctor app:app --profile container

# Validate a profile without importing application code
edron deploy-check --profile reverse-proxy --format json
```

`edron check --format sarif` produces CI-friendly findings. `app.manifest()` and
`app.conformance()` return deterministic, bounded reports for promotion and release gates.

## Moving from Streamlit

Edron offers familiar page, input, metric, data, and chart vocabulary without emulating
Streamlit's global rerun runtime or mutable session dictionary.

```bash
edron migrate streamlit streamlit_app.py --out migrated-app
```

Migration is static and review-first: Edron does not execute the source application or overwrite
it. The output includes a fresh project, deterministic findings, a source map, and explicit TODOs
for behavior that requires human judgment.

[Read the migration center](https://hedron.readthedocs.io/en/latest/guides/streamlit-migration/)
for state, caching, form, and deployment guidance.

## One native Hedron application

Edron is an authoring facade, not a parallel runtime:

```text
Edron Page / fragment / action / resource
                    |
                    v
      Hedron page / view / action / dependency
                    |
                    v
        FastAPI + server-rendered HTML + HTMX
```

Use `self.include(native_node)` to place a native Hedron component in a page. Use `app.native` or
`app.hedron` when an integration needs the exact underlying application. This escape hatch does
not create a bridge or duplicate state—the object is the single native authority Edron has used
from the beginning.

If you prefer direct component-tree authoring and FastAPI-native function routes everywhere, use
the [Hedron package](https://pypi.org/project/hedron/) directly.

## Production responsibilities

Edron provides secure defaults and inspectable boundaries; it does not take ownership of your
application's domain or platform:

- Keep authentication and authorization in trusted dependencies and action boundaries.
- Configure a production session secret and a deliberate security profile.
- Use shared state, cache, and job backends for multi-worker deployments.
- Keep transactions, retries, idempotency, and audit persistence in application services.
- Prefer polling for durable job status unless your proxy and backpressure behavior are verified.
- Run deployment checks for the actual topology, root path, proxy trust, and artifact directory.

Start with the [Edron deployment guide](https://hedron.readthedocs.io/en/latest/guides/edron-deployment/)
and the broader [security guide](https://hedron.readthedocs.io/en/latest/guides/security/).

## Learn more

- [Five-minute quick start](https://hedron.readthedocs.io/en/latest/getting-started/edron-quickstart/)
- [Edron user guide](https://hedron.readthedocs.io/en/latest/guides/edron-user-guide/)
- [API by task](https://hedron.readthedocs.io/en/latest/api/EDRON_REFERENCE/)
- [Example catalog](https://hedron.readthedocs.io/en/latest/examples/edron/)
- [Edron API](https://hedron.readthedocs.io/en/latest/api/EDRON/)
- [Getting started](https://hedron.readthedocs.io/en/latest/getting-started/)
- [Cookbook](https://hedron.readthedocs.io/en/latest/guides/cookbook/)
- [Deployment](https://hedron.readthedocs.io/en/latest/guides/edron-deployment/)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/edron)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/edron/CHANGELOG.md)
- [Issues](https://github.com/eddiethedean/hedron/issues)

## License

Edron is available under the [MIT License](https://github.com/eddiethedean/hedron/blob/main/packages/edron/LICENSE).
