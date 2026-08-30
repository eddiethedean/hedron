# hedron-core

[![PyPI](https://img.shields.io/pypi/v/hedron-core.svg)](https://pypi.org/project/hedron-core/)
[![Python](https://img.shields.io/pypi/pyversions/hedron-core.svg)](https://pypi.org/project/hedron-core/)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![Pyright: strict](https://img.shields.io/badge/Pyright-strict-3178c6.svg)](https://microsoft.github.io/pyright/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

`hedron-core` is the framework-neutral HTML renderer. It has no FastAPI, Flask, or Django
dependency.

The stable boundary is deliberately limited to the public API documented for the 1.x line;
undocumented internals and Beta package surfaces are not covered by that compatibility promise.

Building an app? Install [`hedron`](https://pypi.org/project/hedron/) instead. Use this
package if you are writing a host adapter or rendering components outside a web
framework.

**Package maturity:** Stable · **Package line:** `1.0.x` · **Application pin:**
`hedron-core>=1.0.0,<2.0`

**Typing:** Pyright strict. Commit and release CI fail on type errors or warnings over the
complete `hedron_core` source tree.

## Install

```bash
pip install "hedron-core>=1.0.0,<2.0"
# or
uv add "hedron-core>=1.0.0,<2.0"
```

Requires Python 3.10–3.14.

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

MIT. See the [repository license](https://github.com/eddiethedean/hedron/blob/main/LICENSE).
