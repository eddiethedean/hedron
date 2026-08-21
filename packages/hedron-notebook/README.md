# hedron-notebook

[![PyPI](https://img.shields.io/pypi/v/hedron-notebook.svg)](https://pypi.org/project/hedron-notebook/)
[![Python](https://img.shields.io/pypi/pyversions/hedron-notebook.svg)](https://pypi.org/project/hedron-notebook/)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

Server-side notebook preview helper for Hedron.

Run a normal Hedron ASGI app from an authoring notebook with inline iframe and
external-link modes. Distinct from the browser-Python / JupyterLite sandbox in
`hedron-extras`. Install as `hedron-notebook` or via `hedron[notebook]`.

**Package maturity:** Beta tooling-grade (`0.1.x`) · pin `>=0.1.0,<0.2` (localhost preview only)

Default guidance is **localhost-only** development. Hosted or publicly reachable
hosts raise an explicit warning. Preview URLs include an unguessable session token
(`hedron_preview_token` query parameter). The first successful request seeds an
HttpOnly cookie so iframe follow-up requests (assets, HTMX, WebSockets) stay
authorized; `X-Hedron-Preview-Token` is also accepted. Requests without a matching
token are rejected. This package is **not** a Supported production server.

## Install

```bash
pip install "hedron-notebook>=0.1.0,<0.2"
# or
uv add "hedron-notebook>=0.1.0,<0.2"
# via flagship extra:
pip install "hedron[notebook]>=0.56.0,<0.57"
```

Requires Python 3.11–3.14.

Optional server extra (uvicorn):

```bash
pip install "hedron-notebook[server]>=0.1.0,<0.2"
```

## Quick start

```python
from hedron import Hedron, Page, Text
from hedron_notebook import start_preview

app = Hedron(
    title="Notebook demo",
    security="standard",
    session_secret="dev-only",
    explorer="off",
)


@app.page("/")
def home() -> Page:
    return Page(Text("Hello from a notebook preview"), title="Demo")


preview = start_preview(app)
print(preview.url)
# In a Jupyter cell:
# display HTML with preview.iframe_html()
preview.shutdown()
```

## Public API

| Symbol | Role |
|---|---|
| `start_preview(app)` | Start a local preview server for an ASGI app (token-gated) |
| `NotebookPreview` | Handle with `.url`, `.iframe_html()`, `.shutdown()` |
| `wrap_preview_app(app, token)` | ASGI wrapper requiring the preview session token |
| `PreviewTokenGate` | Pure-ASGI middleware used by `start_preview` |

## Links

- [Package docs](https://hedron.readthedocs.io/en/latest/packages/hedron-notebook/)
- [What’s ready](https://hedron.readthedocs.io/en/latest/guides/whats-ready/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-notebook/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-notebook)
- [Issues](https://github.com/eddiethedean/hedron/issues)
- [`hedron`](https://pypi.org/project/hedron/)

## License

MIT. See the [repository license](https://github.com/eddiethedean/hedron/blob/main/LICENSE).
