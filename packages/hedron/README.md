# hedron

[![PyPI](https://img.shields.io/pypi/v/hedron.svg)](https://pypi.org/project/hedron/)
[![Python](https://img.shields.io/pypi/pyversions/hedron.svg)](https://pypi.org/project/hedron/)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

FastAPI-native typed component framework for HTML and HTMX.

Builds on framework-neutral [`hedron-core`](https://pypi.org/project/hedron-core/)
with pages, addressable components, typed actions, CSRF-aware forms, OpenAPI
`text/html` metadata, interaction built-ins (`Lazy`, `Poll`, `Pagination`, …),
caching (`cache_data` / `cache_component`), utility UI, ColorMode persistence,
a thin `Hedron()` application facade, CLI (`new`/`check`/`graph`/`build`/…),
plugin loader, and public `hedron.testing` helpers.

## Install

```bash
pip install "hedron>=0.19.0,<0.20"
# or
uv add "hedron>=0.19.0,<0.20"
```

Optional extras (pin the train):

```bash
pip install "hedron[data]>=0.19.0,<0.20"
pip install "hedron[charts]>=0.1.0,<0.2"   # Alpha
pip install "hedron[dev]>=0.19.0,<0.20"
pip install "hedron[gradio]>=0.1.0,<0.2"   # Alpha
pip install "hedron[browser]>=0.19.0,<0.20"
```

Requires Python 3.11, 3.12, 3.13, or 3.14. Current train: **0.18.0** (Beta).

## Quick start

Prefer the scaffold so you get **Hello from hedron new** and a working **Refresh status**
click (HTMX swaps a small HTML fragment into a declared region):

```bash
# Need uv? https://docs.astral.sh/uv/getting-started/installation/
uvx --from "hedron>=0.19.0,<0.20" hedron new my-hedron-app
cd my-hedron-app && uv sync && uv run uvicorn app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) — click **Refresh status**; the
timestamp should update.

Full walkthrough: [Build your first app](https://hedron.readthedocs.io/en/latest/getting-started/quickstart/).

### Alternate — static Hello (no Refresh)

This snippet is a **static** page only (no HTMX Refresh). Prefer the scaffold above for
the interactive first-hour experience.

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
pip install "hedron>=0.19.0,<0.20" "uvicorn[standard]"
uvicorn app:app --reload
```

Plain FastAPI without the `Hedron` subclass:

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

CLI inspection (optionally load an app module first):

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

## Links

- [Documentation](https://hedron.readthedocs.io/en/latest/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron)
- [`hedron-core`](https://pypi.org/project/hedron-core/) · [`hedron-explorer`](https://pypi.org/project/hedron-explorer/) · [`hedron-sample-kit`](https://pypi.org/project/hedron-sample-kit/)

## License

MIT. See [LICENSE](LICENSE).
