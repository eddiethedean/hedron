# Hedron

[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![Docs](https://readthedocs.org/projects/hedron/badge/?version=latest)](https://hedron.readthedocs.io/en/latest/?badge=latest)
[![PyPI](https://img.shields.io/pypi/v/hedron.svg?label=hedron)](https://pypi.org/project/hedron/)
[![Python](https://img.shields.io/pypi/pyversions/hedron.svg)](https://pypi.org/project/hedron/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)
[![Release](https://img.shields.io/github/v/release/eddiethedean/hedron.svg)](https://github.com/eddiethedean/hedron/releases/latest)

Hedron is a Python-first framework for building typed, server-rendered component
applications with FastAPI, HTML, and HTMX—without requiring Node.js.

**Current train:** [`v0.10.0`](https://hedron.readthedocs.io/en/latest/guides/whats-ready/)
(live interaction on the FastAPI flagship). Next capability phase: **0.11**.
[What’s new](https://hedron.readthedocs.io/en/latest/guides/whats-new-0.10/) ·
[Upgrade](https://hedron.readthedocs.io/en/latest/guides/upgrade/) ·
[How to read the docs](https://hedron.readthedocs.io/en/latest/getting-started/how-to-read/).

## Five-minute start

```bash
pip install "hedron>=0.10.0"
hedron new my-hedron-app
cd my-hedron-app
uv sync   # or: pip install -e .
uv run uvicorn app:app --reload
```

Or hand-write a page:

```python
from hedron import Hedron, Page, Text

app = Hedron(title="Demo", security="standard", session_secret="replace-me")


@app.page("/")
def home() -> Page:
    return Page(Text("Hello, Hedron"), title="Demo")
```

Docs: [quickstart](https://hedron.readthedocs.io/en/latest/getting-started/quickstart/) ·
[forms & actions](https://hedron.readthedocs.io/en/latest/guides/forms-and-actions/) ·
[why Hedron](https://hedron.readthedocs.io/en/latest/guides/why-hedron/).

## Packages

| Package | Maturity | Role |
|---|---|---|
| [`hedron`](https://pypi.org/project/hedron/) | Beta | FastAPI flagship |
| [`hedron-core`](https://pypi.org/project/hedron-core/) | Beta | Framework-neutral renderer |
| [`hedron-explorer`](https://pypi.org/project/hedron-explorer/) | Beta | Dev Component Explorer (`hedron[dev]`) |
| [`hedron-data`](https://pypi.org/project/hedron-data/) | Beta | DataTable / DataEditor (`hedron[data]`) |
| [`hedron-charts`](https://pypi.org/project/hedron-charts/) | Alpha | Charts (`hedron[charts]`) |
| [`hedron-flask`](https://pypi.org/project/hedron-flask/) / [`hedron-django`](https://pypi.org/project/hedron-django/) | Beta | Supported adapters |
| [`hedron-jinja`](https://pypi.org/project/hedron-jinja/) | Beta | Optional HDJ (`.hdj`) templates |

Optional HDJ via `hedron[jinja]`. HDN was removed in 0.9 (stay on 0.8 if needed).

## Product direction

React-like typed composition, Streamlit-like ease for common objects, FastAPI-native
routing/DI/security, ordinary HTML/CSS/HTMX/Web Components, and no Node.js requirement.
Audience: FastAPI CRUD, internal tools, dashboards, forms, admin, and data apps.

Architectural boundaries and non-goals:
[docs architecture](https://hedron.readthedocs.io/en/latest/ARCHITECTURE/).

## Roadmap (summary)

| | |
|---|---|
| **Current** | 0.10 — live interaction (SSE, streaming, WebSockets, Chat/Dialog, preload) |
| **Next** | 0.11 — native Flask/Django depth and bounded QuerySet integration |

Full phase table and gates: [roadmap](https://hedron.readthedocs.io/en/latest/ROADMAP/).

## Documentation

Hosted docs: [hedron.readthedocs.io](https://hedron.readthedocs.io/en/latest/)

- [Getting started](https://hedron.readthedocs.io/en/latest/getting-started/)
- [What’s ready today](https://hedron.readthedocs.io/en/latest/guides/whats-ready/)
- [Guides](https://hedron.readthedocs.io/en/latest/guides/) · [API](https://hedron.readthedocs.io/en/latest/api/)
- [Runnable examples](https://hedron.readthedocs.io/en/latest/examples/runnable/)

Contributor setup: [Contributing](https://hedron.readthedocs.io/en/latest/CONTRIBUTING/).
Security: [SECURITY.md](SECURITY.md).

## License

MIT — see [LICENSE](https://github.com/eddiethedean/hedron/blob/main/LICENSE).
