# Hedron

[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![Docs](https://readthedocs.org/projects/hedron/badge/?version=latest)](https://hedron.readthedocs.io/en/latest/?badge=latest)
[![PyPI](https://img.shields.io/pypi/v/hedron.svg?label=hedron)](https://pypi.org/project/hedron/)
[![Python](https://img.shields.io/pypi/pyversions/hedron.svg)](https://pypi.org/project/hedron/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)
[![Release](https://img.shields.io/github/v/release/eddiethedean/hedron.svg)](https://github.com/eddiethedean/hedron/releases/latest)

Typed, server-rendered Python UI for FastAPI + HTMX — without a Node.js frontend stack.
Build dashboards, admin tools, forms, and CRUD apps from typed components. Packages are
**Beta** — pin versions and see [What’s ready](https://hedron.readthedocs.io/en/latest/guides/whats-ready/).

If `hedron` is not on your PATH after install, see
[installation](https://hedron.readthedocs.io/en/latest/getting-started/installation/)
([FAQ: command not found](https://hedron.readthedocs.io/en/latest/guides/faq/#hedron-command-not-found)).

## Quick start

Scaffold with `hedron new`, then run. Do not also hand-write a second `app.py` over the
scaffold.

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
python -m pip install "hedron>=0.11.0" "uvicorn[standard]"
python -m hedron new my-hedron-app   # or: hedron new …
cd my-hedron-app
python -m pip install -e .
uvicorn app:app --reload
```

Prefer [uv](https://docs.astral.sh/uv/)? Use `uv tool install "hedron>=0.11.0"`, then
`hedron new`, `uv sync`, and `uv run uvicorn app:app --reload`. Full steps:
[installation](https://hedron.readthedocs.io/en/latest/getting-started/installation/).

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) — you should see **Hello from hedron new**.

Prefer not to install locally? [Try with Codespaces / Dev Container](https://hedron.readthedocs.io/en/latest/examples/try-it/).

**Next:** [HTMX interactions](https://hedron.readthedocs.io/en/latest/guides/htmx-interactions/) →
[Minimal form](https://hedron.readthedocs.io/en/latest/guides/minimal-form/) →
[Learning path](https://hedron.readthedocs.io/en/latest/getting-started/learning-path/).
Evaluating? [What’s ready](https://hedron.readthedocs.io/en/latest/guides/whats-ready/).

## Packages

| Package | Maturity | Role |
|---|---|---|
| [`hedron`](https://pypi.org/project/hedron/) | Beta | FastAPI flagship |
| [`hedron-flask`](https://pypi.org/project/hedron-flask/) | Beta | Flask host adapter |
| [`hedron-django`](https://pypi.org/project/hedron-django/) | Beta | Django host adapter |
| [`hedron[data]`](https://pypi.org/project/hedron-data/) → `hedron-data` | Beta | DataTable / DataEditor / QuerySet source |
| [`hedron[jinja]`](https://pypi.org/project/hedron-jinja/) → `hedron-jinja` | Beta | Optional HDJ templates |
| [`hedron[dev]`](https://pypi.org/project/hedron-explorer/) → `hedron-explorer` | Beta | Component Explorer (dev) |
| [`hedron[charts]`](https://pypi.org/project/hedron-charts/) → `hedron-charts` | Alpha | Chart adapters (pin; expect churn) |

Full matrix and install extras: [installation](https://hedron.readthedocs.io/en/latest/getting-started/installation/).

## Product direction

FastAPI-native typed components, HTMX fragments, and secure HTML defaults. Audience:
CRUD, internal tools, dashboards, forms, admin, and data apps.

Flask/Django: Blueprint/`init_app`, AppConfig, forms bridge, and bounded QuerySet DataSource
are Supported in 0.11. Live helpers are capability-labeled; prefer polling behind buffering proxies.

Current train: [`v0.11.0`](https://hedron.readthedocs.io/en/latest/guides/whats-ready/) (Beta).
[What’s ready](https://hedron.readthedocs.io/en/latest/guides/whats-ready/) ·
[Evaluate Hedron](https://hedron.readthedocs.io/en/latest/guides/evaluate/) ·
[Why Hedron](https://hedron.readthedocs.io/en/latest/guides/why-hedron/) ·
[What’s new](https://hedron.readthedocs.io/en/latest/guides/whats-new-0.10/).

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
