import os

from hedron import (
    Hedron,
    InteractionResult,
    OobHost,
    OobUpdate,
    Page,
    Stack,
    html,
)
from hedron_core.interaction import InteractionPolicy

app = Hedron(
    title="OOB swap",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

main = app.region("settings-main", description="Primary settings")
host = app.region("toast-host", description="OOB toast host")


def primary(draft: bool = True):
    return html.div(
        html.strong("Draft settings" if draft else "Settings saved"),
        html.span("Primary region — not saved yet." if draft else "Primary region updated."),
        id=main.id,
        role="status",
    )


def oob_idle():
    return OobHost(
        html.span("Idle"),
        html.span(
            html.strong("#toast-host"),
            html.small("Stable OOB swap root"),
            class_="hedron-sim-oob-label",
        ),
        id=host.id,
    )


def oob_saved():
    return OobHost(
        html.span("Saved"),
        html.span(
            html.strong("#toast-host"),
            html.small("Out-of-band update"),
            class_="hedron-sim-oob-label",
        ),
        id=host.id,
    )


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            primary(True),
            oob_idle(),
            html.button(
                "Save settings",
                type="button",
                **{
                    "hx-post": "/settings",
                    "hx-target": main.selector,
                    "hx-swap": "outerHTML",
                },
            ),
        ),
        title="OOB",
    )


@app.action("/settings", method="POST", fragment_regions=(main, host))
def save() -> InteractionResult:
    return InteractionResult(
        content=primary(False),
        region_id=main.id,
        oob=(OobUpdate(content=oob_saved(), element_id=host.id),),
        policy=InteractionPolicy(declared_regions=(main, host)),
        explanation="Update main and OOB host",
    )
