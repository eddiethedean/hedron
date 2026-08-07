import os

from hedron import Fragment, Hedron, Page, RefreshButton, Stack, html, swap

app = Hedron(
    title="Fragment demo",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

target = app.region("fragment-demo-target")


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            html.div(
                html.span("Draft"),
                html.span(html.strong("Profile"), html.small("Click refresh to inject siblings.")),
                id=target.id,
            ),
            RefreshButton.for_region(
                target,
                href="/profile-fragment",
                label="Refresh fragment",
                swap="innerHTML",
            ),
        ),
        title="Fragment",
    )


@app.fragment("/profile-fragment", region=target)
def refresh():
    return swap(
        Fragment(
            html.span("Saved"),
            html.span(
                html.strong("Profile updated"),
                html.small("Two siblings returned as a Fragment."),
            ),
        )
    )
