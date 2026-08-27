import os

from hedron import Hedron, Page, Stack, html, swap
from hedron_maps import Map

app = Hedron(
    title="Map markers",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)
panel = app.region("places-map", description="Places map")

PLACES = (
    {"id": "ferry", "lat": 37.7955, "lon": -122.3937, "label": "Ferry Building"},
    {"id": "library", "lat": 37.7793, "lon": -122.4159, "label": "Main Library"},
    {"id": "museum", "lat": 37.7857, "lon": -122.4011, "label": "Museum of Modern Art"},
)


def map_panel(markers=PLACES, *, label="All places"):
    return html.div(
        html.strong(label),
        Map(
            center=(37.7858, -122.4064),
            zoom=13,
            title="San Francisco places",
            description="Useful public destinations with a semantic fallback table.",
            markers=markers,
        ),
        id=panel.id,
    )


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            html.button(
                "All places",
                type="button",
                **{"hx-get": "/places", "hx-target": panel.selector, "hx-swap": "outerHTML"},
            ),
            html.button(
                "Civic only",
                type="button",
                **{
                    "hx-get": "/places/civic",
                    "hx-target": panel.selector,
                    "hx-swap": "outerHTML",
                },
            ),
            map_panel(),
        ),
        title="Map markers",
    )


@app.view("/places", fragment_regions=(panel,))
def all_places():
    return swap(map_panel())


@app.view("/places/civic", fragment_regions=(panel,))
def civic_places():
    return swap(map_panel(PLACES[1:], label="Civic places"))
