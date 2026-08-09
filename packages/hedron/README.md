# hedron

[![PyPI](https://img.shields.io/pypi/v/hedron.svg)](https://pypi.org/project/hedron/)
[![Python](https://img.shields.io/pypi/pyversions/hedron.svg)](https://pypi.org/project/hedron/)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

FastAPI-native typed component framework for HTML and HTMX.

Build dashboards, admin tools, and CRUD apps as typed Python components — without a
Node.js frontend stack. Hedron extends FastAPI with pages, addressable components,
typed actions, CSRF-aware forms, HTMX fragment/OOB policy, OpenAPI `text/html`
metadata, interaction built-ins (`Lazy`, `Poll`, `Pagination`, …), caching
(`cache_data` / `cache_component`), ColorMode persistence, a thin `Hedron()`
application facade, CLI (`new` / `check` / `graph` / `build` / …), plugin loading,
and public `hedron.testing` helpers.

Built on framework-neutral [`hedron-core`](https://pypi.org/project/hedron-core/).
Flask and Django hosts use [`hedron-flask`](https://pypi.org/project/hedron-flask/)
and [`hedron-django`](https://pypi.org/project/hedron-django/).

**Package maturity:** Beta · **Train:** `0.25.0` (Published) · pin `>=0.25.0,<0.26`

Most public APIs remain compatibility level `beta` until listed in the small
[stable](https://hedron.readthedocs.io/en/latest/api/STABILITY/) table.
Capability readiness:
[What’s ready today](https://hedron.readthedocs.io/en/latest/guides/whats-ready/).

## Install

```bash
pip install "hedron>=0.25.0,<0.26"
# or
uv add "hedron>=0.25.0,<0.26"
```

Requires Python 3.11–3.14.

### Optional extras

| Extra | Installs |
|---|---|
| `data` | [`hedron-data`](https://pypi.org/project/hedron-data/) (DataTable / DataEditor) |
| `jinja` | [`hedron-jinja`](https://pypi.org/project/hedron-jinja/) (`.hdj` templates) |
| `dev` | [`hedron-explorer`](https://pypi.org/project/hedron-explorer/) (Component Explorer) |
| `extras` | [`hedron-extras`](https://pypi.org/project/hedron-extras/) (workbenches) |
| `conformance` | [`hedron-conformance`](https://pypi.org/project/hedron-conformance/) |
| `charts` | [`hedron-charts`](https://pypi.org/project/hedron-charts/) (**Alpha** `0.1.x`) |
| `native` | [`hedron-native`](https://pypi.org/project/hedron-native/) (**Alpha**) |
| `notebook` / `mcp` / `gradio` | Experimental Alpha packages |
| `markdown` / `code` / `images` / `email` / `sanitize` | Content helpers |
| `auth` | Authlib OIDC helpers |
| `browser` | Playwright + axe helpers |
| `otel` | OpenTelemetry hooks |

```bash
pip install "hedron[data,dev]>=0.25.0,<0.26"
pip install "hedron[charts]>=0.1.0,<0.2"   # Alpha — pin and expect churn
```

## Quick start

Scaffold an app with a working HTMX **Refresh status** control:

```bash
# Need uv? https://docs.astral.sh/uv/getting-started/installation/
uvx --from "hedron>=0.25.0,<0.26" hedron new my-hedron-app
cd my-hedron-app && uv sync && uv run uvicorn app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) — click **Refresh status**; the
timestamp updates via an HTMX fragment swap.

Full walkthrough:
[Build your first app](https://hedron.readthedocs.io/en/latest/getting-started/quickstart/).

### Minimal app

```python
from hedron import Hedron, Page, Text

app = Hedron(
    title="Demo",
    security="standard",
    session_secret="replace-in-production",
    explorer="off",
)


@app.page("/")
def home() -> Page:
    return Page(Text("Hello, Hedron"), title="Demo")
```

```bash
pip install "hedron>=0.25.0,<0.26" "uvicorn[standard]"
uvicorn app:app --reload
```

### Plain FastAPI

```python
from fastapi import FastAPI
from hedron import HTML, HedronRouter, Text, hedron_response, mount_hedron_static
from hedron.security.policy import SecurityPolicy

app = FastAPI()
app.state.hedron_security = SecurityPolicy.from_name("standard")
mount_hedron_static(app)
router = HedronRouter()


@router.get("/card", **hedron_response())
def card():
    return HTML(Text("plain"))


app.include_router(router)
```

### CLI

```bash
hedron new demoapp
cd demoapp
hedron --app app:app routes
hedron --app app:app components
hedron --app app:app preview home
hedron check --format json --severity error
hedron graph
hedron audit-components
```

If `hedron` is not on your `PATH`, use `python -m hedron`.

## Links

- [Documentation](https://hedron.readthedocs.io/en/latest/)
- [Optional packages](https://hedron.readthedocs.io/en/latest/packages/)
- [What’s ready](https://hedron.readthedocs.io/en/latest/guides/whats-ready/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron)
- [Issues](https://github.com/eddiethedean/hedron/issues)
- [`hedron-core`](https://pypi.org/project/hedron-core/) ·
  [`hedron-flask`](https://pypi.org/project/hedron-flask/) ·
  [`hedron-django`](https://pypi.org/project/hedron-django/)

## License

MIT. See [LICENSE](LICENSE).
