import os

from hedron import Hedron, Page, Stack, html, swap
from hedron_maps import GeoJSONLayer, Map

app = Hedron(
    title="Map layers",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)
panel = app.region("operations-map", description="Operations map")


def points(*items):
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": item[0],
                "properties": {"name": item[1]},
                "geometry": {"type": "Point", "coordinates": item[2]},
            }
            for item in items
        ],
    }


INCIDENTS = points(
    ("signal", "Signal repair", [-122.4075, 37.7837]),
    ("street", "Street closure", [-122.4008, 37.7891]),
)
INSPECTIONS = points(("pier", "Pier inspection", [-122.3971, 37.7993]))


def map_panel(data, *, label):
    return html.div(
        html.strong(label),
        Map(
            center=(37.789, -122.404),
            zoom=13,
            title="Operations map",
            description=f"Current layer: {label}.",
            layers=(GeoJSONLayer(data=data),),
        ),
        id=panel.id,
    )


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            html.button(
                "Incidents",
                type="button",
                **{
                    "hx-get": "/layers/incidents",
                    "hx-target": panel.selector,
                    "hx-swap": "outerHTML",
                },
            ),
            html.button(
                "Inspections",
                type="button",
                **{
                    "hx-get": "/layers/inspections",
                    "hx-target": panel.selector,
                    "hx-swap": "outerHTML",
                },
            ),
            map_panel(INCIDENTS, label="Active incidents"),
        ),
        title="Map layers",
    )


@app.view("/layers/incidents", fragment_regions=(panel,))
def incidents():
    return swap(map_panel(INCIDENTS, label="Active incidents"))


@app.view("/layers/inspections", fragment_regions=(panel,))
def inspections():
    return swap(map_panel(INSPECTIONS, label="Scheduled inspections"))
