# Flask adapter quickstart

Use `hedron-flask` when your app is Flask-native. The adapter renders the same
`hedron-core` components and `InteractionResult` values as the FastAPI flagship—without
installing FastAPI.

## Install

```bash
uv init my-flask-app && cd my-flask-app
uv add hedron-flask
```

Or: `pip install hedron-flask`.

## Minimal app

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
uv run flask --app app:app run --debug
```

## CSRF

Safe GETs issue the `hedron_csrf` cookie. Unsafe methods on `hedron_route` and
`HedronFlask.respond` require a matching `X-CSRF-Token` header or `csrf_token` form field.

## Next

- [Flask reference example](https://github.com/eddiethedean/hedron/tree/main/examples/flask-reference)
- [Security](../guides/security.md) · [Deployment](../guides/deployment.md) · [Adapters API](../api/ADAPTERS.md)
- Deferred: official HTMX SSE (use polling for job status)
