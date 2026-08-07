"""Minimal native Flask reference slice (factory + Blueprint)."""

from __future__ import annotations

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
        Heading("Hedron Flask Reference", level=1),
        Text("Native Flask routing with Hedron components."),
        title="Flask Reference",
    )


@ui.component("/fragment", fragment_regions=(PANEL,))
def fragment():
    return InteractionResult(content=Text("HTMX fragment refreshed"), explanation="demo fragment")


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
