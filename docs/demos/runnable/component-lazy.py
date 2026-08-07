import os

from hedron import ComponentRef, Hedron, Lazy, Loading, Page, html, swap

app = Hedron(
    title="Lazy demo",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

box = app.region("lazy-box")
ref = ComponentRef(
    logical_id="activity-feed",
    path="/activity-feed",
    target=box.selector,
    swap="innerHTML",
)


@app.page("/")
def home() -> Page:
    return Page(
        Lazy(
            ref=ref,
            placeholder=Loading("Loading account activity…"),
            target_id=box.id,
        ),
        title="Lazy",
    )


@app.fragment("/activity-feed", region=box)
def feed():
    return swap(
        html.div(
            html.strong("3 recent events"),
            html.span("Deployment, approval, and release notes loaded."),
        )
    )
