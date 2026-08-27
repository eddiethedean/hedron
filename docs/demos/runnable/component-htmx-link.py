import os

from hedron import Fragment, Hedron, HtmxLink, MainPanel, Page, Stack, html, swap

app = Hedron(
    title="HtmxLink demo",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

panel = app.region("htmx-link-panel")


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            html.div(
                HtmxLink("Reports", "/reports", target=panel.selector, swap="innerHTML"),
                HtmxLink("Team", "/team", target=panel.selector, swap="innerHTML"),
            ),
            MainPanel(
                html.strong("Choose a link"),
                html.span("HtmxLink keeps href as the progressive-enhancement path."),
                id=panel.id,
            ),
        ),
        title="HtmxLink",
    )


@app.view("/reports", fragment_regions=(panel,))
def reports():
    return swap(
        Fragment(
            html.strong("Reports"),
            html.span("In-shell navigation with SafeUrl href fallback."),
        )
    )


@app.view("/team", fragment_regions=(panel,))
def team():
    return swap(
        Fragment(
            html.strong("Team"),
            html.span("Ordinary href still works without JavaScript."),
        )
    )
