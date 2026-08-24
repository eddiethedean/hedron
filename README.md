# Hedron

[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![Docs](https://readthedocs.org/projects/hedron/badge/?version=latest)](https://hedron.readthedocs.io/en/latest/?badge=latest)
[![PyPI](https://img.shields.io/pypi/v/hedron.svg?label=hedron)](https://pypi.org/project/hedron/)
[![Python](https://img.shields.io/pypi/pyversions/hedron.svg)](https://pypi.org/project/hedron/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)
[![Release](https://img.shields.io/github/v/release/eddiethedean/hedron.svg)](https://github.com/eddiethedean/hedron/releases/latest)

Hedron lets you build admin tools, CRUD apps, and dashboards in Python on FastAPI.
Routes return Python components; HTMX swaps HTML fragments. No Node frontend.

**Requires Python 3.11–3.14.** Prefer [uv](https://docs.astral.sh/uv/getting-started/installation/).
**You only need the `hedron` package** (+ uvicorn). Optional packages are listed below.

The latest installable PyPI release is `0.60.0`; the repository train is `0.60.x`.
Application pins and extras:
[Installation](https://hedron.readthedocs.io/en/latest/getting-started/installation/).

```bash
# Need uv? macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows (PowerShell): irm https://astral.sh/uv/install.ps1 | iex

uvx --from "hedron>=0.60.0,<0.61" hedron new my-hedron-app
cd my-hedron-app && uv sync && uv run uvicorn app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) — you should see **Hello from hedron new**.
Click **Refresh status**; the page updates without a full reload (HTMX swaps a small HTML
fragment into the declared region).

![Hello from hedron new with Refresh status control](docs/assets/hello-refresh.jpg)

Full walkthrough:
[First app](https://hedron.readthedocs.io/en/latest/getting-started/quickstart/).

Alternate (pip + venv):

```bash
# macOS / Linux
python3 -m venv .venv && source .venv/bin/activate
python -m pip install "hedron>=0.60.0,<0.61" "uvicorn[standard]"
python -m hedron new my-hedron-app
cd my-hedron-app && python -m pip install -e . && uvicorn app:app --reload
```

```powershell
# Windows (PowerShell)
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install "hedron>=0.60.0,<0.61" "uvicorn[standard]"
python -m hedron new my-hedron-app
cd my-hedron-app
python -m pip install -e .
uvicorn app:app --reload
```

If PowerShell reports that running scripts is disabled, use
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or activate with
`.\.venv\Scripts\activate.bat` from cmd.exe.

If `hedron` is not on your PATH, use `python -m hedron`
([install notes](https://hedron.readthedocs.io/en/latest/getting-started/installation/)).

**Next:** [First app](https://hedron.readthedocs.io/en/latest/getting-started/quickstart/) →
[Minimal form](https://hedron.readthedocs.io/en/latest/guides/minimal-form/) →
[What is HTMX?](https://hedron.readthedocs.io/en/latest/getting-started/what-is-htmx/) →
[Learning path](https://hedron.readthedocs.io/en/latest/getting-started/learning-path/).

Pins and support status: [Current release](https://hedron.readthedocs.io/en/latest/guides/current-release/).

## Who it’s for

CRUD, admin, dashboards, and forms as Python components on FastAPI — when you want HTMX fragment
regions, CSRF defaults, and multi-worker job status **without** assembling a hand-rolled
Jinja+HTMX stack. Prefer `@app.screen` for new apps.

Flask and Django hosts are supported via `hedron-flask` / `hedron-django` (pin versions).
Live SSE/WebSocket helpers are experimental — prefer polling behind buffering proxies.
Packages are **Beta** — pin a minor range (`>=0.60.0,<0.61`). For production fit, read
[What’s ready](https://hedron.readthedocs.io/en/latest/guides/whats-ready/); for Hello,
keep going below.

Coming from Streamlit? Use the
[Streamlit migration center](https://hedron.readthedocs.io/en/latest/guides/streamlit-migration/).

### When not to choose Hedron

Prefer Streamlit for notebook-style rerun dashboards, or raw FastAPI+HTMX if you do not
want a component framework.

[Evaluate Hedron](https://hedron.readthedocs.io/en/latest/guides/evaluate/) ·
[What’s new in 0.60](https://hedron.readthedocs.io/en/latest/guides/whats-new-0.60/) ·
[Current release](https://hedron.readthedocs.io/en/latest/guides/current-release/) ·
[Changelog](https://hedron.readthedocs.io/en/latest/guides/changelog/).

Existing apps on older lines: [Upgrade](https://hedron.readthedocs.io/en/latest/guides/upgrade/).

[Architecture](https://hedron.readthedocs.io/en/latest/ARCHITECTURE/) ·
[Documentation map](https://hedron.readthedocs.io/en/latest/guides/documentation-map/) ·
[What’s next](https://hedron.readthedocs.io/en/latest/guides/whats-next/).

## Packages

| Package | Role |
|---|---|
| [`hedron`](https://pypi.org/project/hedron/) | FastAPI flagship |
| [`hedron-flask`](https://pypi.org/project/hedron-flask/) | Flask host adapter |
| [`hedron-django`](https://pypi.org/project/hedron-django/) | Django host adapter |
| [`hedron-data`](https://pypi.org/project/hedron-data/) | DataTable / DataEditor (also `pip install "hedron[data]>=0.60.0,<0.61"`) |
| [`hedron-jinja`](https://pypi.org/project/hedron-jinja/) | Optional HDJ templates (also `hedron[jinja]`) |
| [`hedron-explorer`](https://pypi.org/project/hedron-explorer/) | Component Explorer (also `hedron[dev]`) |

Full catalog: [packages](https://hedron.readthedocs.io/en/latest/packages/).

Flagship and adapters are **Beta** package maturity on PyPI — pin versions. Optional extras
(data, charts, Jinja, conformance, curated UI, native acceleration, notebook, MCP, Gradio,
Web Components, Workbench, and Posit):
[installation](https://hedron.readthedocs.io/en/latest/getting-started/installation/).

Charts: `pip install "hedron[charts]>=0.60.0,<0.61"`.
Maps: `pip install "hedron[maps]>=0.60.0,<0.61"`.
Plugin authors can install `hedron-sample-kit>=0.2.0,<0.3`. Older satellite releases target
older cores; see [Compatibility](https://hedron.readthedocs.io/en/latest/COMPATIBILITY/#charts-and-sample-kit-compatibility-floor).

Prefer not to install locally? Use a **full cloud environment** (not a hosted playground) —
[Codespaces / Dev Container](https://hedron.readthedocs.io/en/latest/examples/try-it/)
(first boot often **5–15 minutes**, then run the same scaffold commands).
[![Open in GitHub Codespaces](https://img.shields.io/badge/Codespaces-~10%2B%20min%20first%20boot-blue?logo=github)](https://codespaces.new/eddiethedean/hedron)

## What you get

| Need | Hedron provides |
|---|---|
| Server-rendered UI | Pages, layouts, forms, tables, and status components rendered as HTML |
| Partial-page interaction | Declared HTMX regions and fragments with target allowlists and progressive-enhancement paths |
| FastAPI integration | Ordinary routes, dependency injection, middleware, lifespan, and JSON endpoints alongside UI routes |
| Safer defaults | Contextual escaping, CSRF profiles, explicit URL/HTML trust boundaries, and conservative caching |
| Production building blocks | Testing helpers, diagnostics, polling jobs, deployment guidance, and Flask/Django adapters |

Hedron is **not** an ORM, identity provider, hosted service, or client-side SPA runtime.
Your application still owns authentication, authorization, persistence, tenancy, and
deployment. SSE and WebSocket helpers are experimental; use polling unless you have
validated proxy buffering, timeouts, and backpressure for your environment.

## Documentation

Hosted docs: [hedron.readthedocs.io](https://hedron.readthedocs.io/en/latest/)

- [Getting started](https://hedron.readthedocs.io/en/latest/getting-started/)
- [Cookbook](https://hedron.readthedocs.io/en/latest/guides/cookbook/) — pasteable patterns
- [Troubleshooting](https://hedron.readthedocs.io/en/latest/guides/troubleshooting/)
- [Try with Codespaces](https://hedron.readthedocs.io/en/latest/examples/try-it/)
- [What’s ready today](https://hedron.readthedocs.io/en/latest/guides/whats-ready/)
- [Guides](https://hedron.readthedocs.io/en/latest/guides/) · [API](https://hedron.readthedocs.io/en/latest/api/)
- [Runnable examples](https://hedron.readthedocs.io/en/latest/examples/runnable/)

Contributor setup: [Contributing](https://hedron.readthedocs.io/en/latest/CONTRIBUTING/).
Security: [SECURITY.md](SECURITY.md).

## License

MIT — see [LICENSE](https://github.com/eddiethedean/hedron/blob/main/LICENSE).
