"""Minimal native Flask reference slice (factory + Blueprint)."""

from __future__ import annotations

from datetime import datetime, timezone

from flask import Flask

from hedron_core import Heading, Page, Text, html
from hedron_core.interaction import FragmentRegion, InteractionPolicy, InteractionResult
from hedron_flask import HedronBlueprint, HedronFlask

hedron = HedronFlask()
ui = HedronBlueprint("ui", __name__)

PANEL = FragmentRegion(id="panel", selector="#panel")


def panel_body():
    stamp = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    return html.div(Text(f"Flask status · {stamp}"), id="panel")


@ui.page("/")
def home():
    return Page(
        Heading("Hedron Flask Reference", level=1),
        Text("Native Flask routing with Hedron components."),
        panel_body(),
        html.button(
            Text("Refresh"),
            **{
                "hx-get": "/fragment",
                "hx-target": "#panel",
                "hx-swap": "outerHTML",
            },
        ),
        title="Flask Reference",
    )


@ui.view("/fragment", fragment_regions=(PANEL,))
def fragment():
    return InteractionResult(
        content=panel_body(),
        region_id="panel",
        policy=InteractionPolicy(declared_regions=(PANEL,)),
        explanation="demo fragment",
    )


def create_app() -> Flask:
    """Application factory returning the native Flask application."""
    app = Flask(__name__)
    app.secret_key = "flask-reference"
    hedron.init_app(app)
    app.register_blueprint(ui)
    return app


app = create_app()


if __name__ == "__main__":
    # Port 8000 matches Codespaces / try-it forwarding and the FastAPI demos.
    app.run(debug=True, host="127.0.0.1", port=8000)
