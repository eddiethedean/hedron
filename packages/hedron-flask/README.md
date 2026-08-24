# hedron-flask

[![PyPI](https://img.shields.io/pypi/v/hedron-flask.svg)](https://pypi.org/project/hedron-flask/)
[![Python](https://img.shields.io/pypi/pyversions/hedron-flask.svg)](https://pypi.org/project/hedron-flask/)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

Flask adapter for Hedron component rendering and HTMX interactions.

Render `Page` / fragment components with the same [`hedron-core`](https://pypi.org/project/hedron-core/)
renderer used by FastAPI, map portable `InteractionResult` values to native Flask
responses, and integrate CSRF double-submit cookies with Flask sessions. Does **not**
install FastAPI.

**Package maturity:** Beta · **Train:** `0.62.x` (published `v0.62.0` in-tree and on PyPI) · application pin `>=0.62.0,<0.63`; repository checkouts use `uv sync`

Adapter capability readiness is **Supported** when pinned — see
[What’s ready](https://hedron.readthedocs.io/en/latest/guides/whats-ready/).

## Install

```bash
pip install "hedron-flask>=0.62.0,<0.63"
# or
uv add "hedron-flask>=0.62.0,<0.63"
```

Requires Python 3.11–3.14, `hedron-core`, and Flask 3.x.

Scaffold a new Flask app:

```bash
uvx --from "hedron>=0.62.0,<0.63" hedron new --flask my-flask-app
```

## Quick start

```python
from flask import Flask
from hedron_core import Heading, Page, Text
from hedron_core.interaction import FragmentRegion, InteractionResult
from hedron_flask import HedronBlueprint, HedronFlask

hedron = HedronFlask()
ui = HedronBlueprint("ui", __name__)
PANEL = FragmentRegion(id="panel", selector="#panel")


@ui.page("/")
def home():
    return Page(
        Heading("Hello Flask", level=1),
        Text("Native Flask routing with Hedron components."),
        title="Home",
    )


@ui.component("/fragment", fragment_regions=(PANEL,))
def fragment():
    return InteractionResult(content=Text("Fragment ok"), explanation="demo")


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = "replace-in-production"
    hedron.init_app(app)
    app.register_blueprint(ui)
    return app
```

```bash
flask --app app:create_app run --reload
```

## What this package includes

- `HedronFlask` / `init_app` application integration
- `HedronBlueprint` with `@page` / `@component` / `@action` style routing
- `component_response` / `interaction_response` helpers
- Fragment region authorization and approved HTMX header merging
- Portable `SecurityPolicy` headers and Flask-Login `AuthSignal` bridge
- Job status polling helpers (`poll_status_response`)

## Links

- [Add to an existing Flask app](https://hedron.readthedocs.io/en/latest/getting-started/flask/)
- [Adapters API](https://hedron.readthedocs.io/en/latest/api/ADAPTERS/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-flask/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-flask)
- [Issues](https://github.com/eddiethedean/hedron/issues)
- [Flask reference example](https://github.com/eddiethedean/hedron/tree/main/examples/flask-reference)
- [`hedron-core`](https://pypi.org/project/hedron-core/) ·
  [`hedron`](https://pypi.org/project/hedron/) ·
  [`hedron-django`](https://pypi.org/project/hedron-django/)

## License

MIT. See the [repository license](https://github.com/eddiethedean/hedron/blob/main/LICENSE).
