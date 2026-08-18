# Django — greenfield or existing project

Use `hedron-django` for Django-native apps. Requires **Django `>=5.2,<6`**.
The **CLI** (`hedron new --django`) comes from the `hedron` package; **runtime** is
`hedron-django` + `hedron-core`. The adapter does **not** install FastAPI.
It mounts `/hedron-static` so PAGE responses can inject bundled HTMX.

Install from PyPI: `hedron>=0.48.0,<0.49` (or `hedron-django>=0.48.0,<0.49`).
Pins: [Installation](installation.md).

## Golden path (scaffold + Refresh)

Same success criteria as FastAPI: open the app, see Hello, click **Refresh**, watch
the status region update without a full page reload. The scaffold uses Django views
and raw `hx-*` attributes, not FastAPI `RefreshButton`.

```bash
# Need uv? https://docs.astral.sh/uv/getting-started/installation/
uvx --from "hedron>=0.48.0,<0.49" hedron new my-django-app --django
cd my-django-app && uv sync
uv run waitress-serve --listen=127.0.0.1:8000 wsgi:application
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000/) — you should see
**Hello from hedron new --django**. Click **Refresh**; the panel timestamp updates
via HTMX into the declared `#panel` region.

The scaffold includes page + fragment regions and security headers middleware.
Set `HEDRON_SESSION_SECRET` before production.

!!! note "RefreshButton vs raw `hx-*`"

    FastAPI scaffolds often use `RefreshButton`. Django getting-started samples may show
    raw `hx-get` / `hx-target` attributes — both are valid across adapters.

!!! tip "Try without local setup"

    Open the monorepo in [Codespaces / Dev Container](../examples/try-it.md), then
    scaffold with `hedron new my-app --django` or run the reference slice below.

## Alternate: clone the reference

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
cd examples/django-reference
uv run waitress-serve --listen=127.0.0.1:8000 wsgi:application
```

Open `http://127.0.0.1:8000/`. Source:
[`examples/django-reference`](https://github.com/eddiethedean/hedron/tree/main/examples/django-reference).
ASGI: `uv run uvicorn asgi:application --host 127.0.0.1 --port 8000`.

## Existing Django project (add a Refresh page)

```bash
pip install "hedron-django>=0.49.1,<0.50" "django>=5.2,<6"
```

Add `hedron_django` to `INSTALLED_APPS` when you need forms/QuerySet helpers.
Keep `SessionMiddleware` and `CsrfViewMiddleware` for production Django CSRF.

Minimal Refresh-capable view:

```python
# demo/views.py
from datetime import UTC, datetime

from django.http import HttpRequest
from django.urls import path

from hedron_core import FragmentRegion, InteractionResult, Page, Text, html
from hedron_core.interaction import InteractionPolicy
from hedron_django import hedron_view

PANEL = FragmentRegion(id="panel", selector="#panel")


def panel_body() -> object:
    stamp = datetime.now(UTC).strftime("%H:%M:%S UTC")
    return html.div(Text(f"Django status · {stamp}"), id="panel")


@hedron_view
def home(request: HttpRequest):
    return Page(
        html.div(
            Text("Hello Django"),
            panel_body(),
            html.button(
                Text("Refresh"),
                **{
                    "hx-get": "/status",
                    "hx-target": "#panel",
                    "hx-swap": "outerHTML",
                },
            ),
        ),
        title="Home",
    )


@hedron_view(fragment_regions=(PANEL,))
def status(request: HttpRequest):
    return InteractionResult(
        content=panel_body(),
        region_id="panel",
        policy=InteractionPolicy(declared_regions=(PANEL,)),
    )


urlpatterns = [
    path("", home, name="home"),
    path("status", status, name="status"),
]
```

Wire `urlpatterns` into your `ROOT_URLCONF`, then `python manage.py runserver`.

## Portable CSRF header

`HedronDjango.validate_csrf` accepts both Django's `X-CSRFToken` and Hedron's portable
`X-CSRF-Token`. For stock Django middleware alone, HTMX clients that send only the portable
header should set::

```python
CSRF_HEADER_NAME = "HTTP_X_CSRF_TOKEN"
```

in Django settings (as the reference app does).
Stock Django's `X-CSRFToken` remains valid if you keep the default.
**Form posts must use `csrfmiddlewaretoken`.** Django's `CsrfViewMiddleware` does **not**
accept Hedron's portable `csrf_token` field name.

## Next

Stay on Django: extend `@hedron_view` and POST with `csrfmiddlewaretoken`. Prefer
[polling](../guides/live-interaction.md) for job status.

!!! warning "FastAPI-only continuation"

    [HTMX interactions](../guides/htmx-interactions.md) and
    [Minimal form](../guides/minimal-form.md) assume `Hedron()` / `CsrfField()`
    (`csrf_token`). Use them after you switch hosts.

- [Security](../guides/security.md) · [Ship a Hedron app](../guides/ship.md)
- Forms: `hedron_django.forms.form_to_nodes` / `validation_interaction`
- QuerySets: `hedron_data.DjangoQuerySetDataSource` with an already-authorized base QS
