# hedron-explorer

[![PyPI](https://img.shields.io/pypi/v/hedron-explorer.svg)](https://pypi.org/project/hedron-explorer/)
[![Python](https://img.shields.io/pypi/pyversions/hedron-explorer.svg)](https://pypi.org/project/hedron-explorer/)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

Development Component Explorer for Hedron (`v0.4.0`).

Provides HTMX panels for components, routes, graph, security, accessibility,
packages, and settings, plus sanitized JSON APIs with rate limiting and audit
hooks. Installed through `hedron[dev]`; not required in production.

## Install

```bash
pip install "hedron[dev]"
# or
uv add hedron --extra dev
```

Requires Python 3.11, 3.12, 3.13, or 3.14. Depends on
[`hedron`](https://pypi.org/project/hedron/).

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

Then open the Explorer route published by the app (see
[Explorer acceptance](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/EXPLORER.md)).

## Links

- [Documentation](https://hedron.readthedocs.io/en/latest/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-explorer/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron)
- [`hedron`](https://pypi.org/project/hedron/)

## License

MIT. See [LICENSE](LICENSE).
