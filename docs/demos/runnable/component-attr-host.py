import os

from hedron import AttrHost, Hedron, Page, Stack, html, swap

app = Hedron(
    title="AttrHost demo",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

host = app.region("demo-attr-host")


def host_node(state: str):
    return AttrHost(
        html.strong("Attr host"),
        html.small(f"data-state={state}"),
        id=host.id,
        attrs={"data-state": state},
    )


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            host_node("idle"),
            html.button(
                "Run attribute update",
                type="button",
                **{
                    "hx-get": "/status-attrs",
                    "hx-target": host.selector,
                    "hx-swap": "outerHTML",
                },
            ),
        ),
        title="AttrHost",
    )


@app.view("/status-attrs", fragment_regions=(host,))
def attrs():
    return swap(host_node("ready"))
