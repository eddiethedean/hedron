import os

from hedron import FormErrors, Hedron, InteractionResult, Page, Stack, html

app = Hedron(
    title="FormErrors demo",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

region = app.region("errors-demo")
slot = app.region("errors-slot")


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            html.div(
                html.p("Submit with missing fields to redisplay FormErrors."),
                html.div(id=slot.id),
                html.button(
                    "Submit empty form",
                    type="button",
                    **{
                        "hx-post": "/invite",
                        "hx-target": slot.selector,
                        "hx-swap": "innerHTML",
                    },
                ),
                id=region.id,
            ),
        ),
        title="FormErrors",
    )


@app.component("/invite", methods=["POST"], fragment_regions=(region, slot))
def fail() -> InteractionResult:
    return InteractionResult(
        content=FormErrors(["Email is required.", "Choose a billing plan."]),
        status_code=422,
        region_id=slot.id,
    )
