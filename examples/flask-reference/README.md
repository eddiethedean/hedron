# Hedron Flask reference

Minimal **native Flask** slice: home page + HTMX fragment route. Depends on
`hedron-flask` / `hedron-core` only (no FastAPI).

## Prerequisites

- Python 3.11–3.14
- From a Hedron monorepo checkout: `uv sync` (includes adapter extras)

Or in a fresh project:

```bash
pip install "hedron-flask>=0.30.0,<0.31"
# Optional ASGI bridge only if you intentionally serve Flask via uvicorn:
# pip install "uvicorn[standard]"
```

For the built-in development server, `hedron-flask` is enough (`flask --app … run`).

## Run

From the repository root:

```bash
uv sync
uv run python examples/flask-reference/app.py
```

Or with the factory (file path — this tree is not an importable package):

```bash
uv run flask --app examples/flask-reference/app:create_app run --host 127.0.0.1 --port 8000 --debug
```

Open <http://127.0.0.1:8000/> (`python …/app.py` and the factory both use port **8000**).
Fragment: `GET /fragment` (add `HX-Request: true` for fragment-mode rendering).

CSRF: safe GETs set the `hedron_csrf` cookie. Unsafe methods on `hedron_route` /
`HedronFlask.respond` require matching `X-CSRF-Token` (or `csrf_token` form field).

## Scope

This slice proves portable components and `InteractionResult` on Flask. It is not the
full FastAPI reference application (auth, DataEditor, charts).
