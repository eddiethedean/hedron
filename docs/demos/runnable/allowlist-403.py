import os

from hedron import Hedron, Page, Stack, html, swap

app = Hedron(
    title="Allowlist 403",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

status = app.region("service-status", description="Status panel")


def status_panel():
    return html.div(
        html.strong("Service healthy"),
        html.span("Allowlisted #service-status"),
        id=status.id,
        role="status",
    )


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            status_panel(),
            html.button(
                "Correct #service-status → 200",
                type="button",
                **{
                    "hx-get": "/status",
                    "hx-target": status.selector,
                    "hx-swap": "outerHTML",
                },
            ),
            html.button(
                "Wrong #panel → 403",
                type="button",
                **{
                    "hx-get": "/status",
                    "hx-target": "#panel",
                    "hx-swap": "outerHTML",
                },
            ),
        ),
        title="Allowlist",
    )


@app.view("/status", fragment_regions=(status,))
def refresh():
    return swap(status_panel())
