"""Canonical 1.0 source fixture (intentionally unchanged on the 0.67 bridge)."""

from hedron import Hedron, Interaction, Outcome, Stack, Text, html

app = Hedron(
    title="Phase 1.0 canonical fixture",
    security="standard",
    explorer="off",
    session_secret="canonical-fixture-secret-32-bytes!!",
)


@app.view("/status")
def status():
    return html.div(Text("ready"), id="status")


@app.action("/ping")
def ping():
    return Outcome.success(message="pong")


@app.page("/")
def home():
    return Stack(
        status(),
        html.button(
            "Ping",
            interaction=Interaction.request("ping", method="POST"),
        ),
    )
