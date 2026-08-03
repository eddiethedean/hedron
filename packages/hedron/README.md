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

## Install

```bash
pip install hedron
# or
uv add hedron
```

Development Explorer preview:

```bash
pip install "hedron[dev]"
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

CLI inspection (optionally load an app module first):

```bash
hedron --app myapp:app routes
hedron --app myapp:app components
hedron --app myapp:app preview home
```

## Links

- [Documentation](https://github.com/eddiethedean/hedron/tree/main/docs)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron)
- [`hedron-core`](https://pypi.org/project/hedron-core/) · [`hedron-explorer`](https://pypi.org/project/hedron-explorer/)

## License

MIT. See [LICENSE](LICENSE).
