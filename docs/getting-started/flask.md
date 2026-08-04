# Flask — greenfield or existing app

Use `hedron-flask` when your app is Flask-native. Hedron does **not** ship
`hedron new --flask` yet — create the Flask app yourself (or extend an existing one).
The adapter renders the same `hedron-core` components and `InteractionResult` values as
the FastAPI flagship—without installing FastAPI.

Flask/Django: page + fragment routing and HTMX are Supported in 0.10.1. Native
forms depth ships in **0.11** — use polling for job status today.

## Greenfield (empty folder → hello)

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install "hedron-flask>=0.10.1"
# or: uv init my-flask-app && cd my-flask-app && uv add "hedron-flask>=0.10.1"
```

Save as `app.py`:

```python
from flask import request

from hedron_core import Heading, Page, Text
from hedron_core.interaction import InteractionResult
from hedron_flask import HedronFlask, hedron_route

hedron = HedronFlask(__name__)
app = hedron.flask
app.secret_key = "replace-in-production"


@hedron.route("/")
def home():
    return hedron.respond(
        Page(Heading("Hello Flask", level=1), Text("Typed components on Flask."), title="Home"),
        request,
    )


@hedron_route(app, "/fragment", methods=["GET"])
def fragment():
    return InteractionResult(content=Text("Fragment ok"), explanation="demo")
```

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
- Mutations today: use Flask-native forms + CSRF; Hedron-owned forms depth is **0.11**.
  Job status: use bounded polling (FastAPI SSE helpers are Supported on the flagship
  in 0.10; see [live interaction](../guides/live-interaction.md))
- FastAPI scaffold path: [Installation](installation.md) (`hedron new`)
