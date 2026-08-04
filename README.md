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

> **Project status:** Phase **0.10** is published as **`v0.10.0`**. Live interaction (SSE, focused
> streaming, WebSocket channels, Chat/Dialog, navigation preload) ships per RFC-0032. Phase 0.9
> introduced HDJ and removed HDN. Next capability phase: **0.11**.

> **Authoring direction:** [RFC-0031](https://hedron.readthedocs.io/en/latest/rfcs/RFC-0031-JINJA-INTEGRATION/)
> defines HDJ, the optional explicit `.hdj` format over Jinja/HTML/HTMX for trusted application
> authors. Native HTML, CSS, JavaScript, and Web Components remain available; Hedron adds typed
> bridges without hiding the web platform. D-041 removes HDN with no compatibility layer.

**Package maturity:** `hedron`, `hedron-core`, `hedron-explorer`, `hedron-data`,
`hedron-flask`, `hedron-django`, and `hedron-jinja` are Beta. `hedron-charts` and
`hedron-sample-kit` remain Alpha.

## Packages

| Package | Maturity | Role | Install |
|---|---|---|---|
| [`hedron`](https://pypi.org/project/hedron/) | Beta | FastAPI flagship (pages, HTMX, security, CLI) | `pip install hedron` |
| [`hedron-core`](https://pypi.org/project/hedron-core/) | Beta | Framework-neutral typed rendering core | `pip install hedron-core` |
| [`hedron-explorer`](https://pypi.org/project/hedron-explorer/) | Beta | Dev Component Explorer | `pip install "hedron[dev]"` |
| [`hedron-data`](https://pypi.org/project/hedron-data/) | Beta | DataTable, DataEditor, data sources | `pip install "hedron[data]"` or `hedron-data` |
| [`hedron-charts`](https://pypi.org/project/hedron-charts/) | Alpha | Visualization adapters | `pip install "hedron[charts]"` or `hedron-charts` |
| [`hedron-flask`](https://pypi.org/project/hedron-flask/) | Beta | Flask adapter (Supported) | `pip install hedron-flask` |
| [`hedron-django`](https://pypi.org/project/hedron-django/) | Beta | Django adapter (Supported) | `pip install hedron-django` |
| `hedron-jinja` | Beta | HDJ: explicit advanced `.hdj` templates over Jinja/HTML/HTMX | `pip install hedron-jinja` |
| [`hedron-sample-kit`](https://pypi.org/project/hedron-sample-kit/) | Alpha | Sample third-party plugin package | `pip install hedron-sample-kit` |

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
uv add hedron "uvicorn[standard]"
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

Contributor checkout (monorepo only) is documented in [Contributing](https://hedron.readthedocs.io/en/latest/CONTRIBUTING/).

## Roadmap

Phase 0.0 publishes no package. Each capability phase `0.N` maps to initial release `v0.N.0`;
phase 0.10 therefore maps to `v0.10.0`. No 1.0 milestone is scheduled.

| Phase | Initial release | Outcome |
|---|---|---|
| 0.0 | None | Accepted specification and project foundation |
| 0.1 | `v0.1.0` | Framework-neutral typed rendering core (**complete**) |
| 0.2 | `v0.2.0` | Secure FastAPI and HTMX application MVP (**published**) |
| 0.3 | `v0.3.0` | Scoped styles, assets, themes, and experimental HDN prototype (**published**) |
| 0.4 | `v0.4.0` | Explorer, CLI, testing, plugins, and component-author platform (**published**) |
| 0.5 | `v0.5.0` | Data applications, intelligent rendering, caching, and utility UI (**published**) |
| 0.6 | `v0.6.0` | Visualization and first-party integrations (**published**) |
| 0.7 | `v0.7.0` | Portable adapters, Flask/Django, jobs, and operations (**published**) |
| 0.8 | `v0.8.0` | Hardening, stability classification, and compatibility baseline (**published**) |
| 0.9 | `v0.9.0` | HDJ authoring and complete HDN removal (**published**) |
| 0.10 | `v0.10.0` | Live interaction, focused streaming, and navigation preload (**published**) |
| 0.11 | `v0.11.0` | Native Flask/Django depth and bounded QuerySet integration |
| 0.12 | `v0.12.0` | Advanced data editing, distributed sources, and visualization scale |
| 0.13 | `v0.13.0` | Advanced async preparation, concurrency, and observability |
| 0.14 | `v0.14.0` | Portable runtimes and profiling-backed acceleration |
| 0.15 | `v0.15.0` | Data-app surface completeness: controls, media, chat-adjacent ergonomics, identity, and connections |
| 0.16 | `v0.16.0` | Curated optional extras, interactive analysis workbenches, media tools, and isolated browser sandboxes |
| 0.17 | `v0.17.0` | Reactive dashboards, bounded property patches, notebook previews, and explicit agent interfaces |
| 0.18 | `v0.18.0` | Typed model demos, governed inference scheduling and feedback, Gradio interoperability, and visual inference workflows |
| 0.19 | `v0.19.0` | Accessibility contracts, inclusive authoring assistance, interaction/AT evidence, and conformance governance |

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
- Feature cross-checks for [Streamlit](https://hedron.readthedocs.io/en/latest/STREAMLIT_FEATURE_CROSSCHECK/),
  [streamlit-extras](https://hedron.readthedocs.io/en/latest/STREAMLIT_EXTRAS_FEATURE_CROSSCHECK/),
  [Plotly Dash](https://hedron.readthedocs.io/en/latest/PLOTLY_DASH_FEATURE_CROSSCHECK/),
  and [Gradio](https://hedron.readthedocs.io/en/latest/GRADIO_FEATURE_CROSSCHECK/)
- [Accessibility feature research](https://hedron.readthedocs.io/en/latest/ACCESSIBILITY_FEATURE_RESEARCH/)

Build locally:

```bash
uv sync --group docs
uv run mkdocs serve
```

The specification remains the authority for implementation:

- [Specification index](https://hedron.readthedocs.io/en/latest/SPECIFICATION/)
- [Current status](https://hedron.readthedocs.io/en/latest/STATUS/)
- [Architecture](https://hedron.readthedocs.io/en/latest/ARCHITECTURE/), [decisions](https://hedron.readthedocs.io/en/latest/DECISIONS/), and [project layout](https://hedron.readthedocs.io/en/latest/PROJECT_LAYOUT/)
- [Foundations](https://hedron.readthedocs.io/en/latest/foundations/) and [RFC index](https://hedron.readthedocs.io/en/latest/rfcs/)
- [Public API contracts](https://hedron.readthedocs.io/en/latest/api/)
- [Implementation specifications](https://hedron.readthedocs.io/en/latest/implementation/)
- [Acceptance specifications](https://hedron.readthedocs.io/en/latest/acceptance/)
- [Compatibility policy](https://hedron.readthedocs.io/en/latest/COMPATIBILITY/) and [engineering baseline](https://hedron.readthedocs.io/en/latest/ENGINEERING_BASELINE/)
- [Cutting a release](https://hedron.readthedocs.io/en/latest/RELEASE/)

Accepted RFC and API status means the design has been selected; it does not mean every feature is implemented. Availability follows the roadmap phase.

## Current release

**PyPI (install today):** latest published train is **0.10.x** (`pip install hedron`).

**Current train:** coordinated packages are **`0.10.0`** — live interaction on top of the 0.9
HDN-to-HDJ authoring break. Version **0.8** remains the final line for applications that still need
HDN; there is no HDN compatibility switch on 0.9+.

Install `hedron` for the FastAPI flagship, `hedron-flask` / `hedron-django` for Supported
adapters, and `"hedron[data]"`, `"hedron[charts]"`, or `"hedron[jinja]"` for optional subsystems.
Phase `0.10` includes official SSE, focused streaming, WebSocket channels, Dialog/Chat, and opt-in
preload; native framework depth moves to 0.11. Later capability phases remain on the `0.x` line —
see the [roadmap](https://hedron.readthedocs.io/en/latest/ROADMAP/).

## Contributing

Read [Contributing](https://hedron.readthedocs.io/en/latest/CONTRIBUTING/) for
code setup (`uv sync`, tests, docs preview) and for specification/RFC process.
Material public API changes still require an architectural decision and an RFC
revision or superseding RFC.

## License

Hedron is released under the [MIT License](https://github.com/eddiethedean/hedron/blob/main/LICENSE).
