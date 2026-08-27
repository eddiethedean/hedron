import os

from hedron import Hedron, OobHost, Page, Stack, Toast, html, swap

app = Hedron(
    title="Toast demo",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

host = app.region("toast-host")


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            html.button(
                "Copy API key",
                type="button",
                **{
                    "hx-post": "/copy-key",
                    "hx-target": host.selector,
                    "hx-swap": "innerHTML",
                },
            ),
            OobHost(id=host.id),
        ),
        title="Toast",
    )


@app.action("/copy-key", method="POST", fragment_regions=(host,))
def copy():
    return swap(Toast("API key copied.", tone="success"))
