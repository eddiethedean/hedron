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
# Need uv? https://docs.astral.sh/uv/getting-started/installation/
# macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh

uvx --from "hedron>=0.20.0,<0.21" hedron new my-hedron-app
cd my-hedron-app && uv sync && uv run uvicorn app:app --reload
```

Until `v0.20.0` is tagged, PyPI still serves **`v0.18.0`** — install from `main` for
Ready-to-cut `0.20.0`, or wait for the cut.

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) — you should see **Hello from hedron new**.
Click **Refresh status**; the page updates without a full reload (HTMX swaps a small HTML
fragment into the declared region).

![Hello from hedron new with Refresh status control](docs/assets/hello-refresh.jpg)

[![Open in GitHub Codespaces](https://img.shields.io/badge/Codespaces-Open-blue?logo=github)](https://codespaces.new/eddiethedean/hedron)

Prefer not to install locally?
[Try with Codespaces / Dev Container](https://hedron.readthedocs.io/en/latest/examples/try-it/).

Alternate (pip + venv):

```bash
python3 -m venv .venv && source .venv/bin/activate   # Windows: py -3 -m venv .venv && .venv\Scripts\Activate.ps1
python -m pip install "hedron>=0.20.0,<0.21" "uvicorn[standard]"
python -m hedron new my-hedron-app
cd my-hedron-app && python -m pip install -e . && uvicorn app:app --reload
```

**Next:** [First app](https://hedron.readthedocs.io/en/latest/getting-started/quickstart/) →
[HTMX](https://hedron.readthedocs.io/en/latest/guides/htmx-interactions/) →
[Minimal form](https://hedron.readthedocs.io/en/latest/guides/minimal-form/) →
[Learning path](https://hedron.readthedocs.io/en/latest/getting-started/learning-path/).

<details>
<summary>Package maturity</summary>

<strong>Hedron 0.20.0</strong> — Ready to cut on <code>main</code> (last published PyPI/git =
<code>v0.18.0</code>); pin with <code>hedron&gt;=0.20.0,&lt;0.21</code> after
<code>v0.20.0</code> is tagged. <strong>Supported</strong> means the capability works on the
current train when pinned; most public APIs remain compatibility level <code>beta</code>
until listed in the small <strong>stable</strong> table —
<a href="https://hedron.readthedocs.io/en/latest/getting-started/how-to-read/">maturity labels</a>.
Capability readiness:
<a href="https://hedron.readthedocs.io/en/latest/guides/whats-ready/">What’s ready</a>.
If <code>hedron</code> is not on your PATH, use <code>python -m hedron</code>
(<a href="https://hedron.readthedocs.io/en/latest/getting-started/installation/">install notes</a>).
</details>

## Packages

| Package | Maturity | Role |
|---|---|---|
| [`hedron`](https://pypi.org/project/hedron/) | Beta | FastAPI flagship |
| [`hedron-flask`](https://pypi.org/project/hedron-flask/) | Beta | Flask host adapter |
| [`hedron-django`](https://pypi.org/project/hedron-django/) | Beta | Django host adapter |
| [`hedron[data]`](https://pypi.org/project/hedron-data/) | Beta | DataTable / DataEditor |
| [`hedron[jinja]`](https://pypi.org/project/hedron-jinja/) | Beta | Optional HDJ templates |
| [`hedron[dev]`](https://pypi.org/project/hedron-explorer/) | Beta | Component Explorer (dev) |

Optional extras (charts, conformance, extras, native accel, notebook, MCP, Gradio):
[installation](https://hedron.readthedocs.io/en/latest/getting-started/installation/).

## Product direction

FastAPI-native typed components, HTMX fragments, and secure HTML defaults. Audience:
CRUD, internal tools, dashboards, forms, admin, and data apps.

Flask/Django adapters (`hedron-flask`, `hedron-django`) ship Blueprint/`init_app`,
AppConfig, forms bridge, and bounded QuerySet DataSource on the Beta package train —
capability readiness is **Supported** for those surfaces (pin versions).
Live SSE/WebSocket helpers are **experimental** — prefer polling behind buffering proxies.
See [What’s ready](https://hedron.readthedocs.io/en/latest/guides/whats-ready/).

[Why Hedron](https://hedron.readthedocs.io/en/latest/guides/why-hedron/) ·
[Evaluate Hedron](https://hedron.readthedocs.io/en/latest/guides/evaluate/) ·
[What’s new](https://hedron.readthedocs.io/en/latest/guides/whats-new-0.19/) ·
[Changelog](https://hedron.readthedocs.io/en/latest/guides/changelog/).

Existing apps on older lines: [Upgrade](https://hedron.readthedocs.io/en/latest/guides/upgrade/).

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
