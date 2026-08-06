# Hedron

[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![Docs](https://readthedocs.org/projects/hedron/badge/?version=latest)](https://hedron.readthedocs.io/en/latest/?badge=latest)
[![PyPI](https://img.shields.io/pypi/v/hedron.svg?label=hedron)](https://pypi.org/project/hedron/)
[![Python](https://img.shields.io/pypi/pyversions/hedron.svg)](https://pypi.org/project/hedron/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)
[![Release](https://img.shields.io/github/v/release/eddiethedean/hedron.svg)](https://github.com/eddiethedean/hedron/releases/latest)

Hedron lets you build dashboards, admin tools, and CRUD apps as typed Python components
on FastAPI + HTMX — without a Node.js frontend stack.

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
python -m pip install "hedron>=0.18.0" "uvicorn[standard]"
python -m hedron new my-hedron-app
cd my-hedron-app
python -m pip install -e .
uvicorn app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) — you should see **Hello from hedron new**.

Packages are **Beta**; pin versions for production. Details:
[What’s ready](https://hedron.readthedocs.io/en/latest/guides/whats-ready/).
If `hedron` is not on your PATH, use `python -m hedron`
([install notes](https://hedron.readthedocs.io/en/latest/getting-started/installation/)).

Prefer [uv](https://docs.astral.sh/uv/)? Use `uvx --from "hedron>=0.18.0" hedron new …`,
then `uv sync` and `uv run uvicorn app:app --reload`. Full steps:
[installation](https://hedron.readthedocs.io/en/latest/getting-started/installation/).

Prefer not to install locally?
[Try with Codespaces / Dev Container](https://hedron.readthedocs.io/en/latest/examples/try-it/).

**Next:** [HTMX interactions](https://hedron.readthedocs.io/en/latest/guides/htmx-interactions/) →
[Minimal form](https://hedron.readthedocs.io/en/latest/guides/minimal-form/) →
[Learning path](https://hedron.readthedocs.io/en/latest/getting-started/learning-path/).

## Packages

| Package | Maturity | Role |
|---|---|---|
| [`hedron`](https://pypi.org/project/hedron/) | Beta | FastAPI flagship |
| [`hedron-flask`](https://pypi.org/project/hedron-flask/) | Beta | Flask host adapter |
| [`hedron-django`](https://pypi.org/project/hedron-django/) | Beta | Django host adapter |
| [`hedron[data]`](https://pypi.org/project/hedron-data/) → `hedron-data` | Beta | DataTable / DataEditor / QuerySet source |
| [`hedron[jinja]`](https://pypi.org/project/hedron-jinja/) → `hedron-jinja` | Beta | Optional HDJ templates |
| [`hedron[dev]`](https://pypi.org/project/hedron-explorer/) → `hedron-explorer` | Beta | Component Explorer (dev) |
| [`hedron[conformance]`](https://pypi.org/project/hedron-conformance/) → `hedron-conformance` | Beta | Language-neutral conformance kit |
| [`hedron[native]`](https://pypi.org/project/hedron-native/) → `hedron-native` | Alpha | Optional Rust HTML-escape accel |
| [`hedron[extras]`](https://pypi.org/project/hedron-extras/) → `hedron-extras` | Beta | Curated extras / workbenches (0.16) |
| [`hedron[charts]`](https://pypi.org/project/hedron-charts/) → `hedron-charts` | Alpha | Chart adapters (pin; expect churn) |
| [`hedron[notebook]`](https://pypi.org/project/hedron-notebook/) → `hedron-notebook` | Alpha | Server-side notebook preview (experimental) |
| [`hedron[mcp]`](https://pypi.org/project/hedron-mcp/) → `hedron-mcp` | Alpha | Deny-by-default MCP projection (experimental) |
| [`hedron[gradio]`](https://pypi.org/project/hedron-gradio/) → `hedron-gradio` | Alpha | Gradio client interop (experimental) |

Full matrix and install extras: [installation](https://hedron.readthedocs.io/en/latest/getting-started/installation/).

## Product direction

FastAPI-native typed components, HTMX fragments, and secure HTML defaults. Audience:
CRUD, internal tools, dashboards, forms, admin, and data apps.

Flask/Django adapters (`hedron-flask`, `hedron-django`) are Supported on the current
train: Blueprint/`init_app`, AppConfig, forms bridge, and bounded QuerySet DataSource.
Live SSE/WebSocket helpers are **experimental** — prefer polling behind buffering proxies.
See [What’s ready](https://hedron.readthedocs.io/en/latest/guides/whats-ready/).

Current train: **0.18.0** (Beta; **Published** as `v0.18.0`). See
[What’s ready](https://hedron.readthedocs.io/en/latest/guides/whats-ready/). ·
[Evaluate Hedron](https://hedron.readthedocs.io/en/latest/guides/evaluate/) ·
[Why Hedron](https://hedron.readthedocs.io/en/latest/guides/why-hedron/) ·
[What’s new](https://hedron.readthedocs.io/en/latest/guides/whats-new-0.18/).

Existing apps on 0.8/0.9/0.10: [Upgrade](https://hedron.readthedocs.io/en/latest/guides/upgrade/).

[Architecture](https://hedron.readthedocs.io/en/latest/ARCHITECTURE/) ·
[Public roadmap](https://hedron.readthedocs.io/en/latest/guides/roadmap/).

## Documentation

Hosted docs: [hedron.readthedocs.io](https://hedron.readthedocs.io/en/latest/)

- [Getting started](https://hedron.readthedocs.io/en/latest/getting-started/)
- [Try with Codespaces](https://hedron.readthedocs.io/en/latest/examples/try-it/)
- [What’s ready today](https://hedron.readthedocs.io/en/latest/guides/whats-ready/)
- [Guides](https://hedron.readthedocs.io/en/latest/guides/) · [API](https://hedron.readthedocs.io/en/latest/api/)
- [Runnable examples](https://hedron.readthedocs.io/en/latest/examples/runnable/)

Contributor setup: [Contributing](https://hedron.readthedocs.io/en/latest/CONTRIBUTING/).
Security: [SECURITY.md](SECURITY.md).

## License

MIT — see [LICENSE](https://github.com/eddiethedean/hedron/blob/main/LICENSE).
