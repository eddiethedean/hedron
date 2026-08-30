import os

from hedron import Hedron, Loading, Page, Stack, html, swap

app = Hedron(
    title="Loading demo",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

box = app.region("loading-target")


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            html.div(Loading("Loading account activity…"), id=box.id),
            html.button(
                "Load activity",
                type="button",
                **{
                    "hx-get": "/activity",
                    "hx-target": box.selector,
                    "hx-swap": "innerHTML",
                },
            ),
        ),
        title="Loading",
    )


@app.view("/activity", fragment_regions=(box,))
def load():
    return swap(
        html.div(
            html.strong("3 events"),
            html.span("Deployment, approval, and release notes."),
            role="status",
        )
    )
