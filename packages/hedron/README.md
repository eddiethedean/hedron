# hedron

[![PyPI](https://img.shields.io/pypi/v/hedron.svg)](https://pypi.org/project/hedron/)
[![Python](https://img.shields.io/pypi/pyversions/hedron.svg)](https://pypi.org/project/hedron/)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

FastAPI-native typed component framework for HTML and HTMX.

Builds on framework-neutral [`hedron-core`](https://pypi.org/project/hedron-core/)
with pages, addressable components, typed actions, CSRF-aware forms, OpenAPI
`text/html` metadata, interaction built-ins (`Lazy`, `Poll`, `Pagination`, …),
and a thin `Hedron()` application facade.

> **Version note:** This repository packages **0.4.0** (CLI `new`/`check`/`graph`,
> plugins, `hedron.testing`, full Explorer). **PyPI currently serves 0.3.0** until
> `v0.4.0` publishes. Docs: [hedron.readthedocs.io](https://hedron.readthedocs.io/en/latest/).

## Install

```bash
pip install hedron
# or
uv add hedron
```

That installs the latest **PyPI** release (0.3.0 today). For 0.4 features before the
tag, install from git/`main` — see the
[installation guide](https://hedron.readthedocs.io/en/latest/getting-started/installation/).

Development Explorer (0.4+):

```bash
pip install "hedron[dev]"
```

Optional browser testing extras (0.4+):

```bash
pip install "hedron[browser]"
```

Requires Python 3.11, 3.12, 3.13, or 3.14.

## Quick start

```python
from hedron import Hedron, Page, Text

app = Hedron(
    title="Demo",
    security="standard",
    session_secret="replace-me",
    explorer="off",
)


@app.page("/")
def home() -> Page:
    return Page(Text("Hello, Hedron"), title="Demo")
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

CLI inspection (**0.4+** / `main`; optionally load an app module first):

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
