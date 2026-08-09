# Hedron

[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![Docs](https://readthedocs.org/projects/hedron/badge/?version=latest)](https://hedron.readthedocs.io/en/latest/?badge=latest)
[![PyPI](https://img.shields.io/pypi/v/hedron.svg?label=hedron)](https://pypi.org/project/hedron/)
[![Python](https://img.shields.io/pypi/pyversions/hedron.svg)](https://pypi.org/project/hedron/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)
[![Release](https://img.shields.io/github/v/release/eddiethedean/hedron.svg)](https://github.com/eddiethedean/hedron/releases/latest)

Hedron lets you build dashboards, admin tools, and CRUD apps as typed Python components
on FastAPI + HTMX — without a Node.js frontend stack.

Unlike Streamlit’s script-rerun model, Hedron returns typed components from FastAPI routes
and swaps HTML fragments with HTMX.

```bash
# Need uv? https://docs.astral.sh/uv/getting-started/installation/
# macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows (PowerShell): irm https://astral.sh/uv/install.ps1 | iex

uvx --from "hedron>=0.24.0,<0.25" hedron new my-hedron-app
cd my-hedron-app && uv sync && uv run uvicorn app:app --reload
```

Prefer a **clean virtualenv** (Supported pins: FastAPI `>=0.141.1,<0.142`, Pydantic
`>=2.13.4,<2.14` — use a fresh env if your project already pins older versions). Pin
production installs with `hedron>=0.24.0,<0.25`.

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) — you should see **Hello from hedron new**.
Click **Refresh status**; the page updates without a full reload (HTMX swaps a small HTML
fragment into the declared region).

![Hello from hedron new with Refresh status control](docs/assets/hello-refresh.jpg)

![Notes form with CSRF and notes-saved counter](docs/assets/notes-form.jpg)

[![Open in GitHub Codespaces](https://img.shields.io/badge/Codespaces-Open-blue?logo=github)](https://codespaces.new/eddiethedean/hedron)

Prefer not to install locally?
[Try with Codespaces / Dev Container](https://hedron.readthedocs.io/en/latest/examples/try-it/)
(still runs a real app in the cloud — not a hosted playground).

Alternate (pip + venv):

```bash
# macOS / Linux
python3 -m venv .venv && source .venv/bin/activate
python -m pip install "hedron>=0.24.0,<0.25" "uvicorn[standard]"
python -m hedron new my-hedron-app
cd my-hedron-app && python -m pip install -e . && uvicorn app:app --reload
```

```powershell
# Windows (PowerShell)
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install "hedron>=0.24.0,<0.25" "uvicorn[standard]"
python -m hedron new my-hedron-app
cd my-hedron-app
python -m pip install -e .
uvicorn app:app --reload
```

**Next:** [First app](https://hedron.readthedocs.io/en/latest/getting-started/quickstart/) →
[What is HTMX](https://hedron.readthedocs.io/en/latest/getting-started/what-is-htmx/) →
[HTMX interactions](https://hedron.readthedocs.io/en/latest/guides/htmx-interactions/) →
[Minimal form](https://hedron.readthedocs.io/en/latest/guides/minimal-form/) →
[Learning path](https://hedron.readthedocs.io/en/latest/getting-started/learning-path/).

<details>
<summary>Package maturity</summary>

Hedron 0.24.0 is published (Beta packages — pin <code>hedron&gt;=0.24.0,&lt;0.25</code>).
Most APIs are compatibility level <code>beta</code>; see
<a href="https://hedron.readthedocs.io/en/latest/guides/whats-ready/">What’s ready</a>
for Supported vs Experimental. If <code>hedron</code> is not on your PATH, use
<code>python -m hedron</code>
(<a href="https://hedron.readthedocs.io/en/latest/getting-started/installation/">install notes</a>).
</details>

## Packages

| Package | Role |
|---|---|
| [`hedron`](https://pypi.org/project/hedron/) | FastAPI flagship |
| [`hedron-flask`](https://pypi.org/project/hedron-flask/) | Flask host adapter |
| [`hedron-django`](https://pypi.org/project/hedron-django/) | Django host adapter |
| [`hedron[data]`](https://pypi.org/project/hedron-data/) | DataTable / DataEditor |
| [`hedron[jinja]`](https://pypi.org/project/hedron-jinja/) | Optional HDJ templates |
| [`hedron[dev]`](https://pypi.org/project/hedron-explorer/) | Component Explorer (dev) |

Flagship and adapters are **Beta** package maturity on PyPI — pin versions. Optional extras
(charts, conformance, extras, native accel, notebook, MCP, Gradio):
[installation](https://hedron.readthedocs.io/en/latest/getting-started/installation/).

## Who it’s for

CRUD, admin, dashboards, and forms as typed Python on FastAPI — when you want HTMX fragment
regions, CSRF defaults, and multi-worker job status **without** assembling a hand-rolled
Jinja+HTMX stack.

Flask and Django hosts are supported via `hedron-flask` / `hedron-django` (pin versions).
Live SSE/WebSocket helpers are experimental — prefer polling behind buffering proxies.
See [What’s ready](https://hedron.readthedocs.io/en/latest/guides/whats-ready/) and
[Why Hedron](https://hedron.readthedocs.io/en/latest/guides/why-hedron/).

### When not to choose Hedron

Prefer Streamlit for notebook-style rerun dashboards, or raw FastAPI+HTMX if you do not
want a component framework.

[Evaluate Hedron](https://hedron.readthedocs.io/en/latest/guides/evaluate/) ·
[What’s new](https://hedron.readthedocs.io/en/latest/guides/whats-new-0.23/) ·
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
