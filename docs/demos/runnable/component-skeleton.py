import os

from hedron import Hedron, Page, Skeleton, Stack, html, swap

app = Hedron(
    title="Skeleton demo",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

box = app.region("skeleton-target")


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            html.div(Skeleton(lines=3), id=box.id),
            html.button(
                "Load profile",
                type="button",
                **{
                    "hx-get": "/profile",
                    "hx-target": box.selector,
                    "hx-swap": "innerHTML",
                },
            ),
        ),
        title="Skeleton",
    )


@app.fragment("/profile", region=box)
def load():
    return swap(
        html.div(
            html.strong("Ada Lovelace"),
            html.span("Platform · Active"),
            role="status",
        )
    )
