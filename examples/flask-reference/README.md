# Hedron Flask reference

Minimal **native Flask** slice: home page + HTMX fragment route. Depends on
`hedron-flask` / `hedron-core` only (no FastAPI).

## Prerequisites

- Python 3.11–3.14
- From a Hedron monorepo checkout: `uv sync` (includes adapter extras)

Or in a fresh project:

```bash
pip install hedron-flask "uvicorn[standard]"
# For the built-in Flask server you only need hedron-flask
```

## Run

From the repository root:

```bash
uv sync
uv run python examples/flask-reference/app.py
```

Or with the factory:

```bash
uv run flask --app examples.flask-reference.app:create_app run --debug
```

Open <http://127.0.0.1:5000/>. Fragment: `GET /fragment` (add `HX-Request: true` for
fragment-mode rendering).

CSRF: safe GETs set the `hedron_csrf` cookie. Unsafe methods on `hedron_route` /
`HedronFlask.respond` require matching `X-CSRF-Token` (or `csrf_token` form field).

## Scope

This slice proves portable components and `InteractionResult` on Flask. It is not the
full FastAPI reference application (auth, DataEditor, charts).
