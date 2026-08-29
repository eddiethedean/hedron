# Hedron

[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![Docs](https://readthedocs.org/projects/hedron/badge/?version=latest)](https://hedron.readthedocs.io/en/latest/)
[![Edron](https://img.shields.io/pypi/v/edron.svg?label=edron)](https://pypi.org/project/edron/)
[![Hedron](https://img.shields.io/pypi/v/hedron.svg?label=hedron)](https://pypi.org/project/hedron/)
[![Python](https://img.shields.io/pypi/pyversions/hedron.svg)](https://pypi.org/project/hedron/)
[![Pyright: strict](https://img.shields.io/badge/Pyright-strict-3178c6.svg)](https://microsoft.github.io/pyright/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Build polished, server-rendered Python applications without maintaining a separate
frontend.**

**Edron 1.0.0 and Hedron 1.0.0 are published on PyPI.** Application pins in this README
stay within the stable `1.0.x` train.

This repository contains two ways to use the same runtime:

- **[Edron](packages/edron/README.md)** is the batteries-included, class-oriented authoring
  layer. Start here for dashboards, internal tools, CRUD applications, data workspaces, and
  teams moving from Streamlit.
- **[Hedron](packages/hedron/README.md)** is the FastAPI-native component framework underneath.
  Use it when you want direct control over component trees, routes, fragments, actions, host
  integration, and framework extensions.

Both paths render accessible HTML on the server, progressively enhance interactions with HTMX,
and preserve one routing, rendering, security, state, and deployment authority.

The stable 1.0 boundary is the package/API contract in
[`release/support-matrix.toml`](release/support-matrix.toml). Charts, maps, native, notebook,
MCP, Gradio, simulation, and other Beta satellites remain opt-in Beta compatibility surfaces;
they are not included in the stable platform guarantee.

```text
Edron pages and workflows       Native Hedron components and routes
             \                    /
              \                  /
               Hedron application
             (FastAPI + HTML + HTMX)
                        |
                 Browser / HTTP client
```

No Node.js toolchain is required. Python 3.10–3.14 is supported. The `hedron-core` and
`hedron` source trees are checked in Pyright strict mode; type errors block both commit and
release workflows. Warning-level typing cleanup is tracked separately until the existing
workspace warning backlog is retired.

## Alpine.js for browser-local behavior

Hedron uses [Alpine.js](https://alpinejs.dev) for small, disposable interactions that belong in
the browser: disclosures, tabs, menus, focus behavior, local bindings, and other presentation
state that does not require a server request. HTMX remains responsible for server interaction,
fragment replacement, and declared request lifecycles; application and domain state remain on the
server.

The stable platform vendors Alpine.js `3.16.3` as a CSP-compatible runtime and serves it
same-origin from Hedron's immutable browser feature plan. Alpine assets are not fetched from a
CDN at runtime, and no Node.js build step is required. Hedron emits Alpine only when a rendered
page demands it and includes only the required, pinned plugins. Use Hedron's typed Alpine
attributes and built-in components rather than injecting arbitrary Alpine expressions.

Read [What is Alpine?](https://hedron.readthedocs.io/en/latest/getting-started/what-is-alpine/)
for the browser/server ownership rule, lifecycle behavior, and extension guidance.

## Start with Edron

Create and run a teaching project with [`uv`](https://docs.astral.sh/uv/):

```bash
uvx --from "edron>=1.0.0,<1.1" edron new sales-app --template dashboard
cd sales-app
uv sync
uv run uvicorn app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). The generated project is ordinary Python:

```python
import edron as ed

app = ed.App(title="Sales", security="standard")


@app.page("/", title="Sales dashboard")
class Home(ed.Page):
    def render(self) -> None:
        self.metric("Orders", 128, delta="+12")
        self.text("A useful page, rendered on the server.")
```

Edron gives you a compact page vocabulary, typed fragments and actions, forms, data workspaces,
charts, maps, resources, caching, jobs, deployment checks, and a review-first Streamlit migration
tool. Install it directly if you already have a project:

```bash
uv add "edron>=1.0.0,<1.1"
# or: python -m pip install "edron>=1.0.0,<1.1"
```

[Read the Edron package guide](packages/edron/README.md) ·
[Build your first Edron app](https://hedron.readthedocs.io/en/latest/getting-started/edron-quickstart/) ·
[Follow the Edron user guide](https://hedron.readthedocs.io/en/latest/guides/edron-user-guide/)

## Use Hedron directly

Choose Hedron when FastAPI-native routes and explicit component composition are the desired API:

```bash
uvx --from "hedron>=1.0.0,<1.1" hedron new operations-app
cd operations-app
uv sync
uv run hedron run app:app --reload
```

The canonical function roles are deliberately small:

```python
from hedron import Hedron, Stack, Text

app = Hedron(title="Operations", security="standard")


@app.view("/status")
def status():
    return Text("All systems operational")


@app.page("/")
def home():
    return Stack(Text("Operations"), status(), status.refresh_button("Refresh status"))
```

Hedron keeps ordinary FastAPI routes, dependency injection, middleware, lifespan hooks, JSON
endpoints, and OpenAPI available beside its UI routes. It also supports Flask and Django through
first-party host adapters.

[Read the Hedron package guide](packages/hedron/README.md) ·
[Build your first Hedron app](https://hedron.readthedocs.io/en/latest/getting-started/quickstart/)

## Choose your layer

| If you want… | Start with |
|---|---|
| A concise, class-oriented API with batteries included | **Edron** |
| Familiar dashboard vocabulary and a Streamlit migration path | **Edron** |
| Direct component-tree composition | **Hedron** |
| Fine-grained FastAPI routing and dependency control | **Hedron** |
| Flask, Django, or a custom host integration | **Hedron** |
| A mixture of high-level pages and low-level components | **Edron**, then use `Page.include()` or `app.native` |

Edron is not a second web framework. Every Edron page, fragment, action, resource, and feature
package lowers into the exact Hedron application available as `app.native` / `app.hedron`.

## What the stack provides

| Concern | Included capability |
|---|---|
| UI authoring | Pages, layouts, forms, tables, dialogs, navigation, media, charts, and maps |
| Interactions | Addressable fragments, typed actions, partial-page swaps, ordinary HTTP fallbacks, and polling |
| Safety | Contextual escaping, explicit URL/HTML trust boundaries, CSRF profiles, target allowlists, and conservative caching |
| Application integration | FastAPI routing, dependency injection, middleware, lifespan, OpenAPI, plus Flask and Django adapters |
| Data and background work | Bounded data workspaces, edit policies, resources, caches, job backends, and status flows |
| Operations | Static diagnostics, manifests, conformance reports, deployment profiles, build tooling, and observability hooks |
| Extension | Feature packages, component packages, Web Components, Jinja/HDJ, and a framework-neutral core |

[See the full Hedron Showcase](https://hedron.readthedocs.io/en/latest/examples/showcase/)
and run the same source locally. It is a complete operations console with app chrome, metrics,
process flow, tables, status surfaces, fragment refresh, and a typed action.

For the smallest first interaction, try the [Hello + Refresh demo](https://hedron.readthedocs.io/en/latest/examples/single-file/).

Edron has its own [full showcase](https://hedron.readthedocs.io/en/latest/examples/edron-showcase/)
with pages, layouts, fragments, actions, charts, tables, tabs, themes, and outcomes. Its runnable
source uses only `edron`, with no Hedron escape hatches, and is the source represented in the docs.

Hedron is not an ORM, identity provider, database, durable job queue, or hosted service. Your
application owns authentication, authorization, persistence, transactions, tenancy, secrets,
audit storage, and deployment decisions. Polling is the conservative production default for job
status; validate proxy buffering and backpressure before selecting SSE or WebSockets.

## Repository map

The monorepo keeps the coordinated packages, documentation, examples, and conformance evidence in
one place.

| Area | Packages and paths |
|---|---|
| Authoring | [`edron`](packages/edron/), [`hedron`](packages/hedron/), [`hedron-core`](packages/hedron-core/) |
| Data and presentation | [`hedron-data`](packages/hedron-data/), [`hedron-charts`](packages/hedron-charts/), [`hedron-maps`](packages/hedron-maps/), [`hedron-jinja`](packages/hedron-jinja/) |
| Hosts and environments | [`hedron-flask`](packages/hedron-flask/), [`hedron-django`](packages/hedron-django/), [`hedron-posit`](packages/hedron-posit/), [`fastapi-workbench`](packages/fastapi-workbench/) |
| Extension and interop | [`hedron-elements`](packages/hedron-elements/), [`hedron-extras`](packages/hedron-extras/), [`hedron-gradio`](packages/hedron-gradio/), [`hedron-mcp`](packages/hedron-mcp/), [`hedron-notebook`](packages/hedron-notebook/) |
| Quality and tooling | [`hedron-explorer`](packages/hedron-explorer/), [`hedron-conformance`](packages/hedron-conformance/), [`hedron-sim`](packages/hedron-sim/), [`hedron-native`](packages/hedron-native/) |
| Learn and verify | [`docs/`](docs/), [`examples/`](examples/), [`tests/`](tests/), [`scripts/`](scripts/) |

See the [complete package catalog](https://hedron.readthedocs.io/en/latest/packages/) and
[compatibility matrix](https://hedron.readthedocs.io/en/latest/COMPATIBILITY/) before combining
independently versioned satellite packages.

## Documentation

- [Choose Edron or Hedron](https://hedron.readthedocs.io/en/latest/getting-started/choose-layer/)
- [Installation](https://hedron.readthedocs.io/en/latest/getting-started/installation/)
- [Edron quick start](https://hedron.readthedocs.io/en/latest/getting-started/edron-quickstart/)
- [Learning path](https://hedron.readthedocs.io/en/latest/getting-started/learning-path/)
- [Edron user guide](https://hedron.readthedocs.io/en/latest/guides/edron-user-guide/)
- [Hedron API](https://hedron.readthedocs.io/en/latest/api/HEDRON/)
- [Edron API](https://hedron.readthedocs.io/en/latest/api/EDRON_REFERENCE/)
- [Cookbook](https://hedron.readthedocs.io/en/latest/guides/cookbook/)
- [Security](SECURITY.md)
- [Deployment](https://hedron.readthedocs.io/en/latest/guides/deployment/)
- [Troubleshooting](https://hedron.readthedocs.io/en/latest/guides/troubleshooting/)
- [Runnable examples](examples/README.md)
- [Architecture](https://hedron.readthedocs.io/en/latest/ARCHITECTURE/)

## Develop the workspace

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync

uv run pytest -q
uv run ruff check packages tests examples
uv run pyright
# Warning-fatal strict gate for the two runtime packages:
bash scripts/ci_checks.sh typing --python 3.12
```

For documentation work:

```bash
uv sync --group docs
uv run --group docs mkdocs build --strict
# Preview locally: uv run --group docs mkdocs serve
```

Start with [CONTRIBUTING.md](CONTRIBUTING.md) for the narrow test commands, CI paths, and pull
request checklist. By participating, you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).
Security reports should follow [SECURITY.md](SECURITY.md), not a public issue.

## License

Hedron and Edron are available under the [MIT License](LICENSE).
