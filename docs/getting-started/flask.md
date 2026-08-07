# Flask — greenfield or existing app

Use `hedron-flask` when your app is Flask-native. Hedron does **not** ship
`hedron new --flask` yet — create the Flask app yourself (or extend an existing one).
The adapter renders the same `hedron-core` components and `InteractionResult` values as
the FastAPI flagship—without installing FastAPI.

Flask/Django page + fragment routing and HTMX are Supported on **0.19.0**. Prefer
`init_app` + `HedronBlueprint` for application factories; the constructor form remains
supported. Use polling for job status on Flask (SSE helpers stay FastAPI-flagship).

!!! tip "Try without local setup"

    Open the monorepo in [Codespaces / Dev Container](../examples/try-it.md), then run the
    Flask reference slice from `examples/flask-reference/README.md`. There is no
    `hedron new --flask` yet — greenfield steps below create the app yourself.

## Greenfield (empty folder → hello)

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install "hedron-flask>=0.19.0,<0.20"
# or: uv init my-flask-app && cd my-flask-app && uv add "hedron-flask>=0.19.0,<0.20"
```

Save as `app.py` (application factory):

```python
from flask import Flask

from hedron_core import Heading, Page, Text
from hedron_core.interaction import InteractionResult
from hedron_flask import HedronBlueprint, HedronFlask

hedron = HedronFlask()
ui = HedronBlueprint("ui", __name__)


@ui.page("/")
def home():
    return Page(Heading("Hello Flask", level=1), Text("Typed components on Flask."), title="Home")


@ui.component("/fragment")
def fragment():
    return InteractionResult(content=Text("Fragment ok"), explanation="demo")


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = "replace-in-production"
    hedron.init_app(app)
    app.register_blueprint(ui)
    return app


app = create_app()
```

Constructor style (`HedronFlask(__name__)`) still works when you do not need a factory.

```bash
flask --app app:app run --debug
# uv users: uv run flask --app app:app run --debug
```

## CSRF

Safe GETs issue the `hedron_csrf` cookie. Unsafe methods on `hedron_route` and
`HedronFlask.respond` require a matching `X-CSRF-Token` header or `csrf_token` form field.

## Next

- Fastest full example: clone and run the
  [Flask reference](https://github.com/eddiethedean/hedron/tree/main/examples/flask-reference)
- [Security](../guides/security.md) · [Deployment](../guides/deployment.md) · [Adapters API](../api/ADAPTERS.md)
- Mutations: Flask-native forms + CSRF, or Hedron forms helpers where you choose them.
  Job status: use bounded **polling** (FastAPI SSE helpers are **experimental** —
  see [What’s ready](../guides/whats-ready.md) and [live interaction](../guides/live-interaction.md))
- FastAPI scaffold path: [Installation](installation.md) (`hedron new`)
