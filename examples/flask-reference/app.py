"""Minimal native Flask reference slice (home page + HTMX fragment)."""

from __future__ import annotations

from flask import request

from hedron_core import Heading, Page, Text
from hedron_core.interaction import InteractionResult
from hedron_flask import HedronFlask, hedron_route

hedron = HedronFlask(__name__, template_folder=None)
app = hedron.flask


@hedron.route("/")
def home():
    return hedron.respond(
        Page(
            Heading("Hedron Flask Reference", level=1),
            Text("Native Flask routing with Hedron components."),
            title="Flask Reference",
        ),
        request,
    )


@hedron_route(app, "/fragment", endpoint="fragment")
def fragment():
    return InteractionResult(content=Text("HTMX fragment refreshed"), explanation="demo fragment")


def create_app() -> HedronFlask:
    return hedron


if __name__ == "__main__":
    app.run(debug=True)
