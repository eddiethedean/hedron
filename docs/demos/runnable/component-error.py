import os

from hedron import ErrorState, Hedron, Page, html, swap

app = Hedron(
    title="ErrorState demo",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

box = app.region("error-box")


@app.page("/")
def home() -> Page:
    return Page(
        html.div(
            ErrorState(
                "Activity could not be loaded.",
                retry_href="/activity",
                retry_label="Retry",
                target=box.selector,
            ),
            id=box.id,
        ),
        title="ErrorState",
    )


@app.view("/activity", fragment_regions=(box,))
def retry():
    return swap(
        html.div(
            html.strong("Activity restored"),
            html.span("The retry returned a successful fragment."),
            id=box.id,
            role="status",
        )
    )
