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
    title="OobHost demo",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

main = app.region("oob-primary")
host = app.region("demo-oob-host")


def primary(*, draft: bool = True):
    return html.div(
        html.strong("Draft profile" if draft else "Profile saved"),
        html.span("Primary region waiting for save." if draft else "Primary region updated."),
        id=main.id,
    )


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            primary(draft=True),
            OobHost(
                html.span("OOB host"),
                html.span(
                    html.strong("#status"),
                    html.small("Stable swap root"),
                    class_="hedron-sim-oob-label",
                ),
                id=host.id,
            ),
            html.button(
                "Save",
                type="button",
                **{
                    "hx-post": "/profile",
                    "hx-target": main.selector,
                    "hx-swap": "outerHTML",
                },
            ),
        ),
        title="OobHost",
    )


@app.component("/profile", methods=["POST"], fragment_regions=(main, host))
def save() -> InteractionResult:
    return InteractionResult(
        content=primary(draft=False),
        region_id=main.id,
        oob=(
            OobUpdate(
                content=OobHost(
                    html.span("Saved"),
                    html.span(
                        html.strong("#status"),
                        html.small("Out-of-band update"),
                        class_="hedron-sim-oob-label",
                    ),
                    id=host.id,
                ),
                element_id=host.id,
            ),
        ),
        policy=InteractionPolicy(declared_regions=(main, host)),
    )
