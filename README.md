# Hedron

[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![Docs](https://readthedocs.org/projects/hedron/badge/?version=latest)](https://hedron.readthedocs.io/en/latest/?badge=latest)
[![PyPI](https://img.shields.io/pypi/v/hedron.svg?label=hedron)](https://pypi.org/project/hedron/)
[![Python](https://img.shields.io/pypi/pyversions/hedron.svg)](https://pypi.org/project/hedron/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)
[![Release](https://img.shields.io/github/v/release/eddiethedean/hedron.svg)](https://github.com/eddiethedean/hedron/releases/latest)

Hedron is a Python-first framework for building typed, server-rendered
component applications with FastAPI, HTML, HTMX, scoped CSS, and optional Web
Components—without requiring Node.js.

> **Project status:** Phase 0.6 is **published** as `v0.6.0` (visualization adapters,
> content/auth extras, typed HTMX interactions, and `hedron-charts`). The project is
> MIT-licensed. The 0.6 behavioral closure gate is green (Plotly/Vega full offline runtime
> pin remains Deferred/experimental). Next milestone: phase 0.7 (framework adapters and
> production operations).

## Packages

| Package | Role | Install |
|---|---|---|
| [`hedron`](https://pypi.org/project/hedron/) | FastAPI flagship (pages, HTMX, security, CLI) | `pip install hedron` |
| [`hedron-core`](https://pypi.org/project/hedron-core/) | Framework-neutral typed rendering core | `pip install hedron-core` |
| [`hedron-explorer`](https://pypi.org/project/hedron-explorer/) | Dev Component Explorer | `pip install "hedron[dev]"` |
| [`hedron-data`](https://pypi.org/project/hedron-data/) | DataTable, DataEditor, data sources | `pip install "hedron[data]"` or `hedron-data` |
| [`hedron-charts`](https://pypi.org/project/hedron-charts/) | Visualization adapters | `pip install "hedron[charts]"` or `hedron-charts` |
| [`hedron-sample-kit`](https://pypi.org/project/hedron-sample-kit/) | Sample third-party plugin package | `pip install hedron-sample-kit` |

## Product direction

Hedron is designed to combine:

- React-like component composition using typed Python contracts;
- Streamlit-like ease for common Python objects, data tools, and charts;
- FastAPI-native routing, dependency injection, security, OpenAPI, lifespan, and async I/O;
- ordinary HTML, CSS, HTTP, HTMX, and standards-based Web Components;
- an inspectable Component Explorer that explains inferred behavior;
- official development and production paths that do not require npm or a JavaScript bundler.

The initial audience is Python teams building FastAPI CRUD applications, internal tools, dashboards, forms, administrative systems, and data applications.

## Architectural boundaries

- `hedron-core` remains independent of FastAPI, Flask, Django, ASGI, and WSGI.
- HTML endpoints return components; JSON endpoints continue to return models.
- Components are renderable by default but become HTTP-addressable only through explicit registration.
- HTMX owns request-and-swap behavior; Web Components own durable browser-local interaction.
- Authorization, persistence, trust, destructive intent, and application state are never inferred.
- Contextual escaping, typed trust boundaries, accessibility contracts, and private authenticated caching are secure defaults.
- Hedron is not an ORM, identity provider, client-side SPA runtime, durable job queue, distributed cache, or whole-script rerun engine.

## Five-minute secure page

See the hosted [quickstart](https://hedron.readthedocs.io/en/latest/getting-started/quickstart/) for a fuller walkthrough.

```bash
uv add hedron
```

```python
from hedron import Hedron, Page, Text

app = Hedron(title="Demo", security="standard", session_secret="replace-me")


@app.page("/")
def home() -> Page:
    return Page(Text("Hello, Hedron"), title="Demo")
```

```bash
uv run uvicorn app:app --reload
```

Open `/` for a full HTML page. Send `HX-Request: true` (or navigate with HTMX) to receive a fragment without the document shell. CSRF cookies are issued on safe GETs and reused; unsafe actions validate `X-CSRF-Token` or a `csrf_token` form field.

## Quick start (`hedron-core` only)

```bash
uv sync
uv run python -c "from hedron_core import Page, Text, RenderMode, render; print(render(Page(Text('Hello'), title='Hi'), mode=RenderMode.PAGE).html)"
uv run pytest -q
```

## Roadmap

Phase 0.0 publishes no package. Each implementation phase maps to an initial release tag; Python package versions omit the leading `v`.

| Phase | Initial release | Outcome |
|---|---|---|
| 0.0 | None | Accepted specification and project foundation |
| 0.1 | `v0.1.0` | Framework-neutral typed rendering core (**complete**) |
| 0.2 | `v0.2.0` | Secure FastAPI and HTMX application MVP (**published**) |
| 0.3 | `v0.3.0` | HDN, scoped styles, assets, and themes (**published**) |
| 0.4 | `v0.4.0` | Explorer, CLI, testing, plugins, and component-author platform (**published**) |
| 0.5 | `v0.5.0` | Data applications, intelligent rendering, caching, and utility UI (**published**) |
| 0.6 | `v0.6.0` | Visualization and first-party integrations (**published**) |
| 0.7 | `v0.7.0` | Flask/Django adapters and production operations |
| 0.8 | `v0.8.0` | Feature-frozen public API baseline and hardening |
| 1.0 | `v1.0.0` | Stable supported Hedron release |

See the complete [roadmap](https://hedron.readthedocs.io/en/latest/ROADMAP/) for scope, feature ownership, RFC assignments, and release gates.

## Documentation

Hosted docs (MkDocs / Read the Docs): [hedron.readthedocs.io](https://hedron.readthedocs.io/en/latest/)

Start here in the published site:

- [Getting started](https://hedron.readthedocs.io/en/latest/getting-started/)
- [Guides](https://hedron.readthedocs.io/en/latest/guides/)
- [HTMX interactions](https://hedron.readthedocs.io/en/latest/guides/htmx-interactions/)
- [API reference](https://hedron.readthedocs.io/en/latest/api/)
- [Architecture](https://hedron.readthedocs.io/en/latest/ARCHITECTURE/)
- [Status](https://hedron.readthedocs.io/en/latest/STATUS/) and [roadmap](https://hedron.readthedocs.io/en/latest/ROADMAP/)

Build locally:

```bash
uv sync --group docs
uv run mkdocs serve
```

The specification remains the authority for implementation:

- [Specification index](https://hedron.readthedocs.io/en/latest/SPECIFICATION/)
- [Current status](https://hedron.readthedocs.io/en/latest/STATUS/) and [pre-coding readiness report](https://hedron.readthedocs.io/en/latest/READINESS_REPORT/)
- [Architecture](https://hedron.readthedocs.io/en/latest/ARCHITECTURE/), [decisions](https://hedron.readthedocs.io/en/latest/DECISIONS/), and [project layout](https://hedron.readthedocs.io/en/latest/PROJECT_LAYOUT/)
- [Foundations](https://hedron.readthedocs.io/en/latest/foundations/) and [RFC index](https://hedron.readthedocs.io/en/latest/rfcs/)
- [Public API contracts](https://hedron.readthedocs.io/en/latest/api/)
- [Implementation specifications](https://hedron.readthedocs.io/en/latest/implementation/)
- [Acceptance specifications](https://hedron.readthedocs.io/en/latest/acceptance/)
- [Compatibility policy](https://hedron.readthedocs.io/en/latest/COMPATIBILITY/) and [engineering baseline](https://hedron.readthedocs.io/en/latest/ENGINEERING_BASELINE/)
- [Cutting a release](https://hedron.readthedocs.io/en/latest/RELEASE/)

Accepted RFC and API status means the design has been selected; it does not mean every feature is implemented. Availability follows the roadmap phase.

## Current release

Install from PyPI: `pip install hedron` (coordinated train `0.6.0`). Use
`pip install "hedron[data]"` for DataTable/DataEditor and
`pip install "hedron[charts]"` for visualization adapters. Next implementation
target is phase 0.7 — see the [roadmap](https://hedron.readthedocs.io/en/latest/ROADMAP/).

## Contributing

Read [Contributing](https://hedron.readthedocs.io/en/latest/CONTRIBUTING/) for
code setup (`uv sync`, tests, docs preview) and for specification/RFC process.
Material public API changes still require an architectural decision and an RFC
revision or superseding RFC.

## License

Hedron is released under the [MIT License](https://github.com/eddiethedean/hedron/blob/main/LICENSE).
