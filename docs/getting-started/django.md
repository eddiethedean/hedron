# Django adapter quickstart

Use `hedron-django` when your app is Django-native. Requires **Django `>=5.2,<6`**.
The adapter does not install FastAPI.

## Install

```bash
uv init my-django-app && cd my-django-app
uv add "hedron-django" "django>=5.2,<6"
```

## Portable CSRF header

For HTMX clients that send Hedron's portable `X-CSRF-Token`, set in Django settings:

```python
CSRF_HEADER_NAME = "HTTP_X_CSRF_TOKEN"
```

Stock Django's `X-CSRFToken` remains valid if you keep the default. Form posts may use
`csrfmiddlewaretoken` or `csrf_token`. Safe GETs through `HedronDjango.respond` /
`hedron_view` call `get_token` so the CSRF cookie is seeded.

## Minimal view

```python
from django.http import HttpRequest
from django.urls import path

from hedron_core import Heading, Page, Text
from hedron_django import HedronDjango, hedron_view

hedron = HedronDjango()


@hedron_view
def home(request: HttpRequest):
    return hedron.respond(
        Page(Heading("Hello Django", level=1), Text("Typed components on Django."), title="Home"),
        request,
    )


urlpatterns = [path("", home, name="home")]
```

Wire `ROOT_URLCONF` and middleware as usual (`SessionMiddleware`, `CsrfViewMiddleware`).
See the [django-reference](https://github.com/eddiethedean/hedron/tree/main/examples/django-reference)
slice for a manage-less demo (`wsgi.py` / `asgi.py`).

## Run

```bash
# WSGI (Waitress is on the Supported matrix)
waitress-serve --listen=127.0.0.1:8000 wsgi:application

# ASGI
uvicorn asgi:application --host 127.0.0.1 --port 8000
```

## Next

- [Security](../guides/security.md) · [Upgrade](../guides/upgrade.md) · [Deployment](../guides/deployment.md)
- Deferred: QuerySet DataSource, Hedron-owned Django forms (apps may use Django forms directly)
