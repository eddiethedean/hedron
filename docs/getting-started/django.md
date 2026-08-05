# Django — greenfield or existing project

Use `hedron-django` for Django-native apps. Requires **Django `>=5.2,<6`**.
The adapter does not install FastAPI. Hedron does **not** ship `hedron new --django` yet.

Flask/Django page + fragment routing and HTMX are Supported on **0.11.0**. Django
forms bridge and bounded QuerySet DataSource are Supported (D-046). Use polling for
job status on Django (SSE helpers stay FastAPI-flagship).

## Fastest path: clone the reference

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
cd examples/django-reference
uv run waitress-serve --listen=127.0.0.1:8000 wsgi:application
```

Open `http://127.0.0.1:8000/`. Source lives in
[`hedron_django_ref`](https://github.com/eddiethedean/hedron/tree/main/examples/django-reference/hedron_django_ref).
ASGI: `uv run uvicorn asgi:application --host 127.0.0.1 --port 8000`.

This reference is manage-less (home + fragment). For a greenfield Django project with
`manage.py`, use the next section.

## Greenfield (empty folder → hello)

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install "django>=5.2,<6" "hedron-django>=0.11.0"
django-admin startproject mysite .
python manage.py startapp demo
```

Wire a Hedron view (example `demo/views.py` + `mysite/urls.py`):

```python
# demo/views.py
from django.http import HttpRequest

from hedron_core import Heading, Page, Text
from hedron_django import HedronDjango, hedron_view

hedron = HedronDjango()


@hedron_view
def home(request: HttpRequest):
    return hedron.respond(
        Page(Heading("Hello Django", level=1), Text("Typed components on Django."), title="Home"),
        request,
    )
```

```python
# mysite/urls.py
from django.urls import path

from demo.views import home

urlpatterns = [path("", home, name="home")]
```

Ensure `SessionMiddleware` and `CsrfViewMiddleware` remain in `MIDDLEWARE`, then:

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Fastest path: existing Django project (PyPI)

```bash
pip install "hedron-django>=0.11.0" "django>=5.2,<6"
# or: uv add "hedron-django>=0.11.0" "django>=5.2,<6"
```

Assume you already have a Django project with `SessionMiddleware` and
`CsrfViewMiddleware`. Register a view:

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

## Portable CSRF header

For HTMX clients that send Hedron's portable `X-CSRF-Token`, set in Django settings:

```python
CSRF_HEADER_NAME = "HTTP_X_CSRF_TOKEN"
```

Stock Django's `X-CSRFToken` remains valid if you keep the default. Form posts may use
`csrfmiddlewaretoken` or `csrf_token`. Safe GETs through `HedronDjango.respond` /
`hedron_view` call `get_token` so the CSRF cookie is seeded.

## Run your own project

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
- Forms: `hedron_django.forms.form_to_nodes` / `validation_interaction` (CSRF helpers included).
- QuerySets: `hedron_data.DjangoQuerySetDataSource` with an already-authorized base QS;
  omit allowlists to deny client sort/filter. For job status use
  [polling](../guides/live-interaction.md).
