# Django adapter quickstart

Use `hedron-django` when your app is Django-native. Requires **Django `>=5.2,<6`**.
The adapter does not install FastAPI.

## Fastest path: clone the reference

From a Hedron checkout (or after cloning the repo):

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
cd examples/django-reference
uv run waitress-serve --listen=127.0.0.1:8000 wsgi:application
```

Open `http://127.0.0.1:8000/`. The slice is manage-less: settings, URLconf, and views live in
[`hedron_django_ref`](https://github.com/eddiethedean/hedron/tree/main/examples/django-reference/hedron_django_ref).
ASGI: `uv run uvicorn asgi:application --host 127.0.0.1 --port 8000`.

With pip instead of the monorepo:

```bash
pip install "hedron-django" "django>=5.2,<6" waitress
# copy examples/django-reference into a working directory, then:
waitress-serve --listen=127.0.0.1:8000 wsgi:application
```

## Portable CSRF header

For HTMX clients that send Hedron's portable `X-CSRF-Token`, set in Django settings:

```python
CSRF_HEADER_NAME = "HTTP_X_CSRF_TOKEN"
```

Stock Django's `X-CSRFToken` remains valid if you keep the default. Form posts may use
`csrfmiddlewaretoken` or `csrf_token`. Safe GETs through `HedronDjango.respond` /
`hedron_view` call `get_token` so the CSRF cookie is seeded.

## Wire into an existing Django project

Assume you already have a Django project (`django-admin startproject …`) with
`SessionMiddleware` and `CsrfViewMiddleware`. Add the packages, then register a view:

```bash
uv add "hedron-django" "django>=5.2,<6"
```

```python
# urls.py (or a urls module pointed at by ROOT_URLCONF)
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

Required middleware (order matters for CSRF/sessions):

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    # … auth and the rest of your stack
]
```

## Run

```bash
# WSGI — install a server explicitly (Waitress is on the Supported matrix)
pip install waitress
waitress-serve --listen=127.0.0.1:8000 wsgi:application

# ASGI
pip install "uvicorn[standard]"
uvicorn asgi:application --host 127.0.0.1 --port 8000
```

## Next

- [Security](../guides/security.md) · [Upgrade](../guides/upgrade.md) · [Deployment](../guides/deployment.md)
- Deferred (not Supported yet): QuerySet DataSource, Hedron-owned Django forms — apps may use
  Django forms and QuerySets directly until phase 0.11
