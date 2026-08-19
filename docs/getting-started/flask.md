# Flask — greenfield or existing app

Use `hedron-flask` when your app is Flask-native. The **CLI** (`hedron new --flask`)
comes from the `hedron` package; **runtime** is `hedron-flask` + `hedron-core`. The
adapter does **not** install or require FastAPI in the app process.

This documentation is **0.50.1**. Pin `hedron>=0.50.1,<0.51` (or `hedron-flask>=0.50.1,<0.51`).
Public-index notes: [Installation](installation.md).

## Golden path (scaffold + Refresh)

Same success criteria as FastAPI: open the app, see Hello, click **Refresh**, watch
the status region update without a full page reload. The scaffold uses Flask
blueprints and raw `hx-*` attributes, not FastAPI `status.refresh_button(...)`.

```bash
# Need uv? https://docs.astral.sh/uv/getting-started/installation/
uvx --from "hedron>=0.50.1,<0.51" hedron new my-flask-app --flask
cd my-flask-app && uv sync && uv run flask --app app run --port 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000/) — you should see
**Hello from hedron new --flask**. Click **Refresh**; the panel timestamp updates
via HTMX into the declared `#panel` region.

!!! note "Port 8000"

    Hedron Flask samples and docs use port **8000** (same as FastAPI) so you can switch
    examples without changing the browser URL. Plain `flask run` defaults to 5000 if you
    omit `--port`.

The scaffold includes page + fragment regions under `security="standard"`.
Set `HEDRON_SESSION_SECRET` before production.

!!! note "`refresh_button` vs raw `hx-*`"

    FastAPI scaffolds use `status.refresh_button(...)`. Flask/Django getting-started samples may
    show raw `hx-get` / `hx-target` attributes on a button — both are valid. Prefer the
    host’s scaffold helpers when present; raw HTMX attrs remain portable across adapters.

!!! tip "Try without local setup"

    Open the monorepo in [Codespaces / Dev Container](../examples/try-it.md), then
    scaffold with `hedron new my-app --flask` or run
    [`examples/flask-reference`](https://github.com/eddiethedean/hedron/tree/main/examples/flask-reference).

## Alternate: manual factory (with Refresh)

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install "hedron-flask>=0.50.1,<0.51"
```

Save as `app.py`:

```python
import os
from datetime import UTC, datetime

from flask import Flask

from hedron_core import FragmentRegion, InteractionResult, Page, Text, html
from hedron_core.interaction import InteractionPolicy
from hedron_flask import HedronBlueprint, HedronFlask

hedron = HedronFlask()
ui = HedronBlueprint("ui", __name__)

PANEL = FragmentRegion(id="panel", selector="#panel")


def panel_body() -> object:
    stamp = datetime.now(UTC).strftime("%H:%M:%S UTC")
    return html.div(Text(f"Flask status · {stamp}"), id="panel")


@ui.page("/")
def home() -> Page:
    return Page(
        html.div(
            Text("Hello Flask"),
            panel_body(),
            html.button(
                Text("Refresh"),
                **{
                    "hx-get": "/status",
                    "hx-target": "#panel",
                    "hx-swap": "outerHTML",
                },
            ),
        ),
        title="Home",
    )


@ui.component("/status", fragment_regions=(PANEL,))
def status() -> InteractionResult:
    return InteractionResult(
        content=panel_body(),
        region_id="panel",
        policy=InteractionPolicy(declared_regions=(PANEL,)),
    )


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = os.environ.get("HEDRON_SESSION_SECRET", "replace-in-production")
    hedron.init_app(app)
    app.register_blueprint(ui)
    return app


app = create_app()
```

```bash
flask --app app:app run --debug --port 8000
# uv users: uv run flask --app app:app run --debug --port 8000
```

Constructor style (`HedronFlask(__name__)`) still works when you do not need a factory
(see the scaffold `app.py`).

## CSRF

Safe GETs issue the `hedron_csrf` cookie. Unsafe methods on `hedron_route` and
`HedronFlask.respond` require a matching `X-CSRF-Token` header or `csrf_token` form field.

## Next

Stay on Flask: extend the scaffold `HedronBlueprint` / `HedronFlask` and keep POST field
`csrf_token`. Job status: prefer bounded **polling** (FastAPI SSE helpers are experimental).

!!! warning "FastAPI-only continuation"

    [HTMX interactions](../guides/htmx-interactions.md) and
    [Minimal form](../guides/minimal-form.md) assume `Hedron()` / `@app.refreshable` /
    `status.refresh_button(...)` / `CsrfField()`. Use them after you switch hosts, not as the Flask
    next step.

- [Security](../guides/security.md) · [Ship a Hedron app](../guides/ship.md)
- [Adapters API](../api/ADAPTERS.md)
- Clone [`examples/flask-reference`](https://github.com/eddiethedean/hedron/tree/main/examples/flask-reference)
