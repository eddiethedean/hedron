# Hedron

[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/hedron.svg?label=hedron)](https://pypi.org/project/hedron/)
[![Python](https://img.shields.io/pypi/pyversions/hedron.svg)](https://pypi.org/project/hedron/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/eddiethedean/hedron.svg)](https://github.com/eddiethedean/hedron/releases/latest)

Hedron is a Python-first framework for building typed, server-rendered
component applications with FastAPI, HTML, HTMX, scoped CSS, and optional Web
Components—without requiring Node.js.

> **Project status:** Phase 0.3 is implemented on `main` at package version
> `0.3.0` and is ready to cut as `v0.3.0` (PyPI still serves `0.2.0` until the
> release tag publishes). HDN, scoped styles, themes, fingerprinted assets,
> `build`/`dev`/`inspect`/`eject`, and a minimal Web Component proof ship on top
> of the FastAPI MVP. The project is MIT-licensed. After `v0.3.0` publishes, the
> next milestone is phase 0.4 (developer platform and ecosystem contracts).

## Packages

| Package | Role | Install |
|---|---|---|
| [`hedron`](https://pypi.org/project/hedron/) | FastAPI flagship (pages, HTMX, security, CLI) | `pip install hedron` |
| [`hedron-core`](https://pypi.org/project/hedron-core/) | Framework-neutral typed rendering core | `pip install hedron-core` |
| [`hedron-explorer`](https://pypi.org/project/hedron-explorer/) | Dev Component Explorer preview | `pip install "hedron[dev]"` |

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
| 0.3 | `v0.3.0` | HDN, scoped styles, assets, and themes (**ready to cut**) |
| 0.4 | `v0.4.0` | Explorer, CLI, testing, plugins, and component-author platform |
| 0.5 | `v0.5.0` | Data applications, intelligent rendering, caching, and utility UI |
| 0.6 | `v0.6.0` | Visualization and first-party integrations |
| 0.7 | `v0.7.0` | Flask/Django adapters and production operations |
| 0.8 | `v0.8.0` | Public API freeze, release candidate, and hardening |
| 1.0 | `v1.0.0` | Stable supported Hedron release |

See the complete [roadmap](ROADMAP.md) for scope, feature ownership, RFC assignments, and release gates.

## Documentation

The specification remains the authority for implementation:

- [Specification index](docs/README.md)
- [Current status](docs/STATUS.md) and [pre-coding readiness report](docs/READINESS_REPORT.md)
- [Architecture](docs/ARCHITECTURE.md), [decisions](docs/DECISIONS.md), and [project layout](docs/PROJECT_LAYOUT.md)
- [Foundations](docs/foundations/README.md) and [RFC index](docs/rfcs/README.md)
- [Public API contracts](docs/api/README.md)
- [Implementation specifications](docs/implementation/README.md)
- [Acceptance specifications](docs/acceptance/README.md)
- [Compatibility policy](docs/COMPATIBILITY.md) and [engineering baseline](docs/ENGINEERING_BASELINE.md)
- [Cutting a release](docs/RELEASE.md)

Accepted RFC and API status means the design has been selected; it does not mean every feature is implemented. Availability follows the roadmap phase.

## Cutting `v0.3.0`

Implementation is complete on `main`. Follow [Cutting a release](docs/RELEASE.md)
to push the annotated `v0.3.0` tag when CI is green. After publish, the next
implementation target is phase 0.4 — see the [roadmap](ROADMAP.md).

## Contributing

Read [CONTRIBUTING.md](docs/CONTRIBUTING.md) before changing an accepted contract. Material changes require an architectural decision and an RFC revision or superseding RFC. Implementations must name their owning RFC, public contract, implementation specification, and acceptance checks.

## License

Hedron is released under the [MIT License](LICENSE).
