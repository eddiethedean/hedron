# hedron-core

[![PyPI](https://img.shields.io/pypi/v/hedron-core.svg)](https://pypi.org/project/hedron-core/)
[![Python](https://img.shields.io/pypi/pyversions/hedron-core.svg)](https://pypi.org/project/hedron-core/)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

Framework-neutral typed rendering core for Hedron.

Defines models, security boundary types, components, the HTML serializer,
`Auto()` intelligent rendering, cache protocols, ColorMode, utility built-ins,
and the public `render(...) -> RenderResult` and request-scoped `RenderSession`
APIs — with **no** FastAPI, Flask, Django, ASGI, or WSGI dependency.

Host adapters share this renderer:

- FastAPI — [`hedron`](https://pypi.org/project/hedron/)
- Flask — [`hedron-flask`](https://pypi.org/project/hedron-flask/)
- Django — [`hedron-django`](https://pypi.org/project/hedron-django/)

**Package maturity:** Beta · **Train:** `0.21.0` (Published) · pin `>=0.21.0,<0.22`

## Install

```bash
pip install "hedron-core>=0.21.0,<0.22"
# or
uv add "hedron-core>=0.21.0,<0.22"
```

Requires Python 3.11–3.14.

## Quick start

```python
from hedron_core import Page, RenderContext, RenderMode, Text, render

result = render(
    Page(Text("Hello, Hedron"), title="Demo"),
    context=RenderContext.standalone(locale="en"),
    mode=RenderMode.PAGE,
)
print(result.html)
```

## What this package includes

- `Model`, `Props`, `FormModel`, `EventPayload`, and `Field`
- Trust boundary types: `Secret`, `TrustedHtml`, `SafeUrl`, `UrlPurpose`
- Component protocol, registry, diagnostics (JSON/SARIF), and deterministic identity
- Context-aware HTML serializer, `render(...) -> RenderResult`, and `RenderSession`
- Scoped CSS, themes, assets, and component discovery helpers
- Built-ins for pages, forms, layout, landmarks, and content
- Framework-neutral plugin metadata and Explorer panel registration helpers
- Portable adapter contracts (`AuthSignal`, capability matrix, URL reverse request)

## What it does not include

- HTTP routing or FastAPI / Flask / Django adapters
- HTMX request handling and CSRF middleware (host packages)
- CLI, Component Explorer UI, charts, or data grids

Prefer [`hedron`](https://pypi.org/project/hedron/) for application work on FastAPI.

## Links

- [Documentation](https://hedron.readthedocs.io/en/latest/)
- [Architecture](https://hedron.readthedocs.io/en/latest/ARCHITECTURE/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-core/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-core)
- [Issues](https://github.com/eddiethedean/hedron/issues)
- [`hedron`](https://pypi.org/project/hedron/)

## License

MIT. See [LICENSE](LICENSE).
