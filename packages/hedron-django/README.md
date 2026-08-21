# hedron-django

[![PyPI](https://img.shields.io/pypi/v/hedron-django.svg)](https://pypi.org/project/hedron-django/)
[![Python](https://img.shields.io/pypi/pyversions/hedron-django.svg)](https://pypi.org/project/hedron-django/)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

Django adapter for Hedron component rendering and HTMX interactions.

Render components as `HttpResponse`, map portable `InteractionResult` values,
reverse URLs via Django’s resolver, and integrate CSRF/session through native
middleware. Shares the [`hedron-core`](https://pypi.org/project/hedron-core/)
renderer with FastAPI and Flask. Does **not** install FastAPI.

Also ships a first-party bounded QuerySet `DataSource` and Django forms bridge —
supply an already-authorized base QuerySet; omitted sort/filter allowlists deny
client refinements.

**Package maturity:** Beta · **Train:** `0.58.x` (published `v0.58.0` on PyPI) · application pin `>=0.58.0,<0.59`; repository checkouts use `uv sync`

Adapter capability readiness is **Supported** when pinned — see
[What’s ready](https://hedron.readthedocs.io/en/latest/guides/whats-ready/).

## Install

```bash
pip install "hedron-django>=0.58.0,<0.59"
# or
uv add "hedron-django>=0.58.0,<0.59"
```

Requires Python 3.11–3.14, `hedron-core`, and Django `>=5.2,<6`.

Install the AppConfig for system checks:

```python
INSTALLED_APPS = [
    # ...
    "hedron_django.apps.HedronDjangoConfig",
]
```

Scaffold a new Django project:

```bash
uvx --from "hedron>=0.58.0,<0.59" hedron new --django my-django-app
```

## Quick start

```python
from django.http import HttpRequest
from hedron_core import Heading, Page, Text
from hedron_django import HedronDjango, hedron_view

hedron = HedronDjango()


@hedron_view
def home(request: HttpRequest):
    return hedron.respond(
        Page(
            Heading("Hello Django", level=1),
            Text("Native Django URLconf with Hedron components."),
            title="Home",
        ),
        request,
    )
```

Wire the view into your URLconf as usual. For HTMX fragments, declare
`fragment_regions` on `@hedron_view` and return an `InteractionResult`.

## What this package includes

- `HedronDjango` / `respond` rendering facade
- `@hedron_view` decorator with fragment-region policy
- `HedronDjangoConfig` system checks
- `HedronSecurityHeadersMiddleware` for portable `SecurityPolicy` headers
- Forms bridge and bounded QuerySet `DataSource`
- Job status polling helpers

## Links

- [Add to an existing Django project](https://hedron.readthedocs.io/en/latest/getting-started/django/)
- [Adapters API](https://hedron.readthedocs.io/en/latest/api/ADAPTERS/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-django/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-django)
- [Issues](https://github.com/eddiethedean/hedron/issues)
- [Django reference example](https://github.com/eddiethedean/hedron/tree/main/examples/django-reference)
- [`hedron-core`](https://pypi.org/project/hedron-core/) ·
  [`hedron`](https://pypi.org/project/hedron/) ·
  [`hedron-flask`](https://pypi.org/project/hedron-flask/)

## License

MIT. See the [repository license](https://github.com/eddiethedean/hedron/blob/main/LICENSE).
