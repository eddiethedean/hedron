# Hedron Django reference

Minimal **native Django** slice (manage-less): home + fragment. Depends on
`hedron-django` / `hedron-core` only (no FastAPI). Django floor: **`>=5.2,<6`**.

## Prerequisites

- Python 3.11–3.14
- From a Hedron monorepo checkout: `uv sync`

Or:

```bash
pip install "hedron-django" "django>=5.2,<6" gunicorn uvicorn
```

## Run (WSGI)

From the repository root (so `examples/django-reference` is on `PYTHONPATH`):

```bash
cd examples/django-reference
uv run python -c "from wsgi import application; print(application)"
# Development with Waitress (Supported WSGI server for Flask/Django matrix):
uv run waitress-serve --listen=127.0.0.1:8000 wsgi:application
```

Or with gunicorn:

```bash
cd examples/django-reference
uv run gunicorn wsgi:application -b 127.0.0.1:8000
```

## Run (ASGI)

```bash
cd examples/django-reference
uv run uvicorn asgi:application --host 127.0.0.1 --port 8000
```

Open <http://127.0.0.1:8000/>. Fragment: `/fragment/`.

## CSRF

This slice sets `CSRF_HEADER_NAME = "HTTP_X_CSRF_TOKEN"` so portable Hedron clients can
send `X-CSRF-Token`. Safe GETs through `HedronDjango.respond` / `hedron_view` seed the
CSRF cookie via Django's `get_token`. Form posts may use `csrfmiddlewaretoken` or
`csrf_token`.

**Do not use the hardcoded `SECRET_KEY` from this demo in production.**

## Scope

Home + fragment only. Full QuerySet DataSource / forms bridge demos live in the package
tests and docs (Supported in 0.11 / D-046)—see [STATUS](../../docs/STATUS.md).
