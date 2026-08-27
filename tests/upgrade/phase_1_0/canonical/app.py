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


# Exercise every closed role constructor without dispatching application work.
# The tuple is part of the canonical import corpus so both bridge versions
# validate payload shape at import time.
CANONICAL_OUTCOMES = (
    Outcome.success(message="ok"),
    Outcome.no_content(),
    Outcome.refresh("status"),
    Outcome.patch("#status", "updated"),
    Outcome.redirect("/status"),
    Outcome.job("job-1"),
    Outcome.validation({"name": "required"}),
    Outcome.conflict("revision-1"),
    Outcome.download("/download/report.csv"),
)


@app.page("/")
def home():
    return Stack(
        status(),
        html.button(
            "Ping",
            interaction=Interaction.request("ping", method="POST"),
        ),
        html.button(
            "Toggle",
            interaction=Interaction.local("toggle", state_keys=("open",)),
        ),
        html.button(
            "Save",
            interaction=Interaction.combined(
                "close",
                "ping",
                state_keys=("open",),
                method="POST",
            ),
        ),
    )
