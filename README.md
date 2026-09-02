<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/eddiethedean/hedron/v1.0/docs/assets/hedron-logo-dark.svg">
    <img src="https://raw.githubusercontent.com/eddiethedean/hedron/v1.0/docs/assets/hedron-logo-light.svg" width="500" alt="Hedron">
  </picture>
</p>

<p align="center">
  <strong>Build production-minded, server-rendered Python interfaces on FastAPI.</strong>
</p>

<p align="center">
  <a href="https://github.com/eddiethedean/hedron/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI" alt="CI"></a>
  <a href="https://hedron.readthedocs.io/en/latest/"><img src="https://readthedocs.org/projects/hedron/badge/?version=latest" alt="Docs"></a>
  <a href="https://pypi.org/project/hedron/"><img src="https://img.shields.io/pypi/v/hedron.svg?label=hedron" alt="Hedron on PyPI"></a>
  <a href="https://pypi.org/project/hedron/"><img src="https://img.shields.io/pypi/pyversions/hedron.svg" alt="Python versions"></a>
  <a href="https://microsoft.github.io/pyright/"><img src="https://img.shields.io/badge/Pyright-strict-3178c6.svg" alt="Pyright strict"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT license"></a>
</p>

Hedron lets Python teams compose pages, components, forms, and partial-page interactions without
maintaining a separate frontend application. It stays inside the FastAPI model: dependency
injection, middleware, lifespan, async I/O, JSON routes, and OpenAPI remain available beside the UI.

**Hedron 1.0.6 is published on PyPI.** The supported Python range is 3.10–3.14.
`hedron>=1.0.0` is the compatibility floor; new applications should prefer
`hedron>=1.0.6,<1.1` and commit a lockfile (or use `hedron==1.0.6` for an exact
reproduction). Review the [compatibility matrix](https://hedron.readthedocs.io/en/latest/COMPATIBILITY/)
before combining independently versioned satellites.

```text
Python pages and components
            │
   page · view · action
            │
   Hedron + FastAPI runtime
            │
 HTML · HTMX · Alpine · HTTP
```

No Node.js toolchain is required. Hedron renders accessible HTML on the server, uses HTMX for
bounded server interactions, and uses Alpine.js for disposable browser-local presentation state.
Application and domain state stay on the server.

## Start in ten minutes

Create and run a project with [`uv`](https://docs.astral.sh/uv/):

```bash
uvx --from "hedron>=1.0.0" hedron new operations-app
cd operations-app
uv sync
uv run hedron run app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). The core application roles are deliberately
small:

```python
from hedron import Hedron, Stack, Text

app = Hedron(title="Operations", security="standard")


@app.view("/status")
def status():
    return Text("All systems operational")


@app.page("/")
def home():
    return Stack(
        Text("Operations"),
        status(),
        status.refresh_button("Refresh status"),
    )
```

The page is server rendered. The button requests only `/status` and swaps that region. The same
application can expose ordinary FastAPI endpoints, dependencies, middleware, and OpenAPI routes.

[Build your first app](https://hedron.readthedocs.io/en/latest/getting-started/quickstart/) ·
[Follow the learning path](https://hedron.readthedocs.io/en/latest/getting-started/learning-path/) ·
[Find an API by task](https://hedron.readthedocs.io/en/latest/api/by-task/)

## What Hedron provides

| Concern | Included capability |
|---|---|
| UI authoring | Pages, layouts, forms, tables, dialogs, navigation, media, charts, and maps |
| Interactions | Addressable views, typed actions, partial-page swaps, HTTP fallbacks, and polling |
| Safety | Contextual escaping, explicit URL/HTML trust boundaries, CSRF profiles, target allowlists, and conservative caching |
| FastAPI integration | Routing, dependency injection, middleware, lifespan, OpenAPI, testing, and mounted-path support |
| Data and background work | Bounded data workspaces, edit policies, resources, caches, job backends, and status flows |
| Operations | Static diagnostics, manifests, conformance reports, deployment checks, and observability hooks |
| Extension | Feature packages, component packages, Web Components, Jinja/HDJ, and a framework-neutral core |

First-party Flask and Django adapters bring the same component model to applications that do not
run FastAPI. Host adapters and tooling packages keep their own maturity and compatibility claims.

## HTMX and Alpine, with one ownership rule

Use HTMX when behavior crosses the server boundary: requests, validation, mutations, fragment
replacement, and declared lifecycle events. Use Alpine.js for browser-local behavior such as
disclosures, tabs, menus, focus, and transient bindings. Do not duplicate application state in the
browser.

Hedron vendors Alpine.js `3.16.3` as a CSP-compatible, same-origin asset and emits it only when a
rendered page demands it. HTMX and Alpine attributes are typed; arbitrary script injection is not
the authoring model.

[Understand HTMX](https://hedron.readthedocs.io/en/latest/getting-started/what-is-htmx/) ·
[Understand Alpine](https://hedron.readthedocs.io/en/latest/getting-started/what-is-alpine/) ·
[Read the interaction boundary](https://hedron.readthedocs.io/en/latest/api/HTMX_ALPINE_BOUNDARY_1_0/)

## See a complete application

The [Hedron Showcase](https://hedron.readthedocs.io/en/latest/examples/showcase/) is a complete
operations console built with the public component, layout, styling, view, and action APIs. Its
documented source is runnable locally and uses the same built-in styling shown in the simulation.

For a smaller progression, use the [notes application path](https://hedron.readthedocs.io/en/latest/examples/build-notes-app/)
or the [single-file examples](https://hedron.readthedocs.io/en/latest/examples/single-file/).

## Production boundaries

Hedron is not an ORM, identity provider, database, durable queue, or hosted service. Your
application owns authorization, persistence, transactions, tenancy, secrets, audit storage, and
deployment decisions. Polling is the conservative production default for job status; validate
proxy buffering and backpressure before selecting SSE or WebSockets.

The stable 1.0 boundary is defined in
[`release/support-matrix.toml`](release/support-matrix.toml): `hedron-core`, `hedron`, `edron`,
`hedron-data`, `hedron-charts`, and `hedron-maps` are Stable. Host adapters, native, notebook, MCP,
Gradio, simulation, and other satellites remain opt-in Beta or tooling-grade surfaces. A `1.0.x`
version line alone does not promote a package or symbol into the stable platform.

Stable-package source trees are checked in Pyright strict mode. Type errors and warning regressions
block commit and release workflows.

[Evaluate Hedron](https://hedron.readthedocs.io/en/latest/guides/evaluate/) ·
[Review what is ready](https://hedron.readthedocs.io/en/latest/guides/whats-ready/) ·
[Ship an application](https://hedron.readthedocs.io/en/latest/guides/ship/)

## Prefer a higher-level facade?

[Take the alternate Edron route](packages/edron/README.md). It provides a class-oriented page API
over the same Hedron application authority. The primary documentation, examples, and API navigation
use Hedron directly.

## Repository map

| Area | Packages and paths |
|---|---|
| Runtime | [`hedron`](packages/hedron/), [`hedron-core`](packages/hedron-core/) |
| Data and presentation | [`hedron-data`](packages/hedron-data/), [`hedron-charts`](packages/hedron-charts/), [`hedron-maps`](packages/hedron-maps/), [`hedron-jinja`](packages/hedron-jinja/) |
| Hosts and environments | [`hedron-flask`](packages/hedron-flask/), [`hedron-django`](packages/hedron-django/), [`hedron-posit`](packages/hedron-posit/), [`fastapi-workbench`](packages/fastapi-workbench/) |
| Extension and interop | [`hedron-elements`](packages/hedron-elements/), [`hedron-extras`](packages/hedron-extras/), [`hedron-gradio`](packages/hedron-gradio/), [`hedron-mcp`](packages/hedron-mcp/), [`hedron-notebook`](packages/hedron-notebook/) |
| Quality and tooling | [`hedron-explorer`](packages/hedron-explorer/), [`hedron-conformance`](packages/hedron-conformance/), [`hedron-sim`](packages/hedron-sim/), [`hedron-native`](packages/hedron-native/) |
| Alternate facade | `edron`, `edron-sim` |
| Learn and verify | [`docs/`](docs/), [`examples/`](examples/), [`tests/`](tests/), [`scripts/`](scripts/) |

See the [complete package catalog](https://hedron.readthedocs.io/en/latest/packages/) before
combining independently versioned packages.

## Documentation

- [Installation](https://hedron.readthedocs.io/en/latest/getting-started/installation/)
- [Build your first app](https://hedron.readthedocs.io/en/latest/getting-started/quickstart/)
- [Learning path](https://hedron.readthedocs.io/en/latest/getting-started/learning-path/)
- [Cookbook](https://hedron.readthedocs.io/en/latest/guides/cookbook/)
- [API by task](https://hedron.readthedocs.io/en/latest/api/by-task/)
- [Hedron API](https://hedron.readthedocs.io/en/latest/api/HEDRON/)
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
bash scripts/ci_checks.sh typing --python 3.12
```

For documentation work:

```bash
uv sync --group docs
uv run --group docs mkdocs build --strict
# Preview locally at http://127.0.0.1:8000/
READTHEDOCS_CANONICAL_URL=http://127.0.0.1:8000/ uv run --group docs mkdocs serve
```

Start with [CONTRIBUTING.md](CONTRIBUTING.md) for the focused checks and pull-request checklist.
Security reports follow [SECURITY.md](SECURITY.md), not a public issue.

## License

Hedron and its coordinated packages are available under the [MIT License](LICENSE).
