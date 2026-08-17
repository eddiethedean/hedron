# Hedron Django reference

Minimal **native Django** slice (manage-less): home + fragment. Depends on
`hedron-django` / `hedron-core` only (no FastAPI). Django floor: **`>=5.2,<6`**.

## Prerequisites

- Python 3.11–3.14
- From a Hedron monorepo checkout: `uv sync`

Or (pip, outside the monorepo):

```bash
pip install "hedron-django>=0.49.0,<0.50" "django>=5.2,<6" "waitress>=3,<4"
```

For ASGI locally you can use `uvicorn` instead of Waitress.

## Run (WSGI)

`wsgi.py` puts this directory on `sys.path`. From the repository root:

```bash
cd examples/django-reference
uv run waitress-serve --listen=127.0.0.1:8000 wsgi:application
```

Waitress is the Supported reference WSGI server for the Flask/Django matrix. If you
prefer gunicorn in your own deploy, install it yourself — it is **not** a workspace
dependency of this monorepo.

## Run (ASGI)

```bash
cd examples/django-reference
uv run uvicorn asgi:application --host 127.0.0.1 --port 8000
```

Open <http://127.0.0.1:8000/>. Click **Refresh** to swap the `#panel` timestamp.
Fragment: `/fragment`.

## CSRF

This slice sets `CSRF_HEADER_NAME = "HTTP_X_CSRF_TOKEN"` so portable Hedron clients can
send `X-CSRF-Token`. Safe GETs through `HedronDjango.respond` / `hedron_view` seed the
CSRF cookie via Django's `get_token`. Form posts may use `csrfmiddlewaretoken` or
`csrf_token`.

**Do not use the hardcoded `SECRET_KEY` from this demo in production.**

## Scope

Home + fragment only. Full QuerySet DataSource / forms bridge demos live in the package
tests and docs (Supported — see [What’s ready](https://hedron.readthedocs.io/en/latest/guides/whats-ready/)).
