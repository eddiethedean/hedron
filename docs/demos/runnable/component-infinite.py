import os

from hedron import ComponentRef, Fragment, Hedron, InfiniteScroll, Page, Stack, html, swap

app = Hedron(
    title="InfiniteScroll demo",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

feed = app.region("event-feed")
ref = ComponentRef(
    logical_id="events",
    path="/events",
    target=feed.selector,
    swap="beforeend",
)


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            html.ol(
                html.li("Deployment completed"),
                html.li("Review approved"),
                id=feed.id,
            ),
            InfiniteScroll(ref=ref, target=feed.selector, swap="beforeend"),
        ),
        title="InfiniteScroll",
    )


@app.view("/events", fragment_regions=(feed,))
def more():
    return swap(Fragment(html.li("Tests passed"), html.li("Release published")))
