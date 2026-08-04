# Hedron

[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![Docs](https://readthedocs.org/projects/hedron/badge/?version=latest)](https://hedron.readthedocs.io/en/latest/?badge=latest)
[![PyPI](https://img.shields.io/pypi/v/hedron.svg?label=hedron)](https://pypi.org/project/hedron/)
[![Python](https://img.shields.io/pypi/pyversions/hedron.svg)](https://pypi.org/project/hedron/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)
[![Release](https://img.shields.io/github/v/release/eddiethedean/hedron.svg)](https://github.com/eddiethedean/hedron/releases/latest)

Typed, server-rendered Python UI for FastAPI + HTMX — without a Node.js frontend stack.
Build dashboards, admin tools, forms, and CRUD apps from typed components.

## Five-minute start

Prefer **one** path: scaffold with `hedron new`, then run. Do not also hand-write a second
`app.py` over the scaffold.

**pip:**

```bash
pip install "hedron>=0.10.0" "uvicorn[standard]"
hedron new my-hedron-app
cd my-hedron-app
pip install -e .
uvicorn app:app --reload
```

**uv:**

```bash
uv tool install "hedron>=0.10.0"   # puts `hedron` on your PATH
hedron new my-hedron-app
cd my-hedron-app
uv sync
uv run uvicorn app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) — you should see the scaffold home page.

If `hedron` is not on your PATH after `pip install`, see
[installation](https://hedron.readthedocs.io/en/latest/getting-started/installation/).

**Next:** [Build your first app](https://hedron.readthedocs.io/en/latest/getting-started/quickstart/) →
[HTMX interactions](https://hedron.readthedocs.io/en/latest/guides/htmx-interactions/) →
[Minimal form](https://hedron.readthedocs.io/en/latest/guides/minimal-form/).

Manual `app.py` (only if you are **not** using `hedron new`):

```python
from hedron import Hedron, Page, Text

app = Hedron(title="Demo", security="standard", session_secret="replace-in-production")


@app.page("/")
def home() -> Page:
    return Page(Text("Hello, Hedron"), title="Demo")
```

## Packages

| Package | Maturity | Role |
|---|---|---|
| [`hedron`](https://pypi.org/project/hedron/) | Beta | FastAPI flagship |
| [`hedron-flask`](https://pypi.org/project/hedron-flask/) / [`hedron-django`](https://pypi.org/project/hedron-django/) | Beta | Host adapters |
| [`hedron[data]`](https://pypi.org/project/hedron-data/) / [`hedron[charts]`](https://pypi.org/project/hedron-charts/) / [`hedron[jinja]`](https://pypi.org/project/hedron-jinja/) / [`hedron[dev]`](https://pypi.org/project/hedron-explorer/) | Beta / Alpha | Optional extras |

Full matrix and install extras: [installation](https://hedron.readthedocs.io/en/latest/getting-started/installation/).

## Product direction

FastAPI-native typed components, HTMX fragments, and secure HTML defaults. Audience:
CRUD, internal tools, dashboards, forms, admin, and data apps. Next release focus:
Flask/Django depth (**0.11**).

Current train: [`v0.10.0`](https://hedron.readthedocs.io/en/latest/guides/whats-ready/) (Beta).
[What’s ready](https://hedron.readthedocs.io/en/latest/guides/whats-ready/) ·
[Evaluate Hedron](https://hedron.readthedocs.io/en/latest/guides/evaluate/) ·
[Why Hedron](https://hedron.readthedocs.io/en/latest/guides/why-hedron/) ·
[What’s new](https://hedron.readthedocs.io/en/latest/guides/whats-new-0.10/) ·
[Upgrade](https://hedron.readthedocs.io/en/latest/guides/upgrade/).

[Architecture](https://hedron.readthedocs.io/en/latest/ARCHITECTURE/) ·
[Public roadmap](https://hedron.readthedocs.io/en/latest/guides/roadmap/).

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
