# hedron-explorer

[![PyPI](https://img.shields.io/pypi/v/hedron-explorer.svg)](https://pypi.org/project/hedron-explorer/)
[![Python](https://img.shields.io/pypi/pyversions/hedron-explorer.svg)](https://pypi.org/project/hedron-explorer/)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

Development Component Explorer for Hedron.

HTMX panels for components, routes, graph, security, accessibility, cache, data,
charts, maps, HTMX extensions, auto, packages, elements, inventory, interactions,
features, settings, and interaction simulation — plus sanitized JSON APIs
(`/api/diff`, `/api/package-health`) with rate limiting and audit hooks. Installed
through `hedron[dev]`; **not required** in production.

**Package maturity:** Beta · **Train:** `0.51.x` (published `v0.51.0`) · pin `>=0.51.0,<0.52`

## Install

```bash
pip install "hedron[dev]>=0.51.0,<0.52"
# or install the package directly:
pip install "hedron-explorer>=0.51.0,<0.52"
# or
uv add "hedron[dev]>=0.51.0,<0.52"
```

Requires Python 3.11–3.14 and [`hedron`](https://pypi.org/project/hedron/).

Optional: `hedron-explorer[fastapi]` when you need an explicit FastAPI extra
marker for tooling (the flagship `hedron` package already depends on FastAPI).

## Usage

Enable the Explorer when constructing the app (development only by default):

```python
from hedron import Hedron, Page, Text

app = Hedron(
    title="Demo",
    security="standard",
    session_secret="replace-me",
    explorer="development",
)


@app.page("/")
def home() -> Page:
    return Page(Text("Hello, Hedron"), title="Demo")
```

Open **`/hedron-explorer/`** on the running app (`explorer="development"` or
`"secured"`). Leave Explorer **`off`** in production.

## What this package includes

- Interactive component / route / dependency graph panels
- Security and accessibility inspection surfaces
- Interaction simulation helpers
- Sanitized JSON APIs with rate limiting and audit hooks

## Links

- [Package docs](https://hedron.readthedocs.io/en/latest/packages/hedron-explorer/)
- [Explorer API](https://hedron.readthedocs.io/en/latest/api/EXPLORER/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-explorer/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-explorer)
- [Issues](https://github.com/eddiethedean/hedron/issues)
- [`hedron`](https://pypi.org/project/hedron/)

## License

MIT. See the [repository license](https://github.com/eddiethedean/hedron/blob/main/LICENSE).
