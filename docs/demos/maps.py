"""Package-native hedron-maps demos rendered through hedron-sim."""

from __future__ import annotations

from hedron import Page, Stack, html, swap
from hedron_maps import GeoJSONLayer, Map
from hedron_sim import SimApp, embed_demo

__all__ = ["build_maps_layers_demo", "build_maps_markers_demo"]


PLACES = (
    {
        "id": "ferry",
        "lat": 37.7955,
        "lon": -122.3937,
        "label": "Ferry Building",
        "href": "/places/ferry",
    },
    {
        "id": "library",
        "lat": 37.7793,
        "lon": -122.4159,
        "label": "Main Library",
        "href": "/places/library",
    },
    {
        "id": "museum",
        "lat": 37.7857,
        "lon": -122.4011,
        "label": "Museum of Modern Art",
        "href": "/places/museum",
    },
)


def _hx(path: str, target: str) -> dict[str, str]:
    return {"hx-get": path, "hx-target": target, "hx-swap": "outerHTML"}


def build_maps_markers_demo() -> str:
    """Filter real ``hedron_maps.Map`` marker plans and their fallback table."""
    app = SimApp(title="Map markers", demo_id="maps-markers")
    panel = app.region("places-map", description="Places map")

    def map_panel(markers=PLACES, *, label: str = "All places"):
        return html.div(
            html.strong(label),
            Map(
                center=(37.7858, -122.4064),
                zoom=13,
                title="San Francisco places",
                description="Three useful public destinations with ordinary fallback links.",
                markers=markers,
            ),
            id=panel.id,
        )

    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                html.div(
                    html.button("All places", type="button", **_hx("/places", panel.selector)),
                    html.button(
                        "Civic only", type="button", **_hx("/places/civic", panel.selector)
                    ),
                    class_="hedron-sim-row",
                ),
                map_panel(),
                html.p(
                    "The docs do not request live tiles; inspect the same server-rendered "
                    "feature table available when the canvas cannot upgrade.",
                    class_="hedron-sim-muted",
                ),
            ),
            title="Map markers",
        )

    @app.fragment("/places", region=panel)
    def all_places():
        return swap(map_panel())

    @app.fragment("/places/civic", region=panel)
    def civic_places():
        return swap(map_panel(PLACES[1:], label="Civic places"))

    return embed_demo(app)


INCIDENTS = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "id": "signal",
            "properties": {"name": "Signal repair"},
            "geometry": {"type": "Point", "coordinates": [-122.4075, 37.7837]},
        },
        {
            "type": "Feature",
            "id": "street",
            "properties": {"name": "Street closure"},
            "geometry": {"type": "Point", "coordinates": [-122.4008, 37.7891]},
        },
    ],
}

INSPECTIONS = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "id": "pier",
            "properties": {"name": "Pier inspection"},
            "geometry": {"type": "Point", "coordinates": [-122.3971, 37.7993]},
        }
    ],
}


def build_maps_layers_demo() -> str:
    """Swap typed GeoJSON layers while retaining their semantic alternative."""
    app = SimApp(title="Map layers", demo_id="maps-layers")
    panel = app.region("operations-map", description="Operations map")

    def map_panel(data: dict, *, label: str):
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
                html.div(
                    html.button(
                        "Incidents", type="button", **_hx("/layers/incidents", panel.selector)
                    ),
                    html.button(
                        "Inspections", type="button", **_hx("/layers/inspections", panel.selector)
                    ),
                    class_="hedron-sim-row",
                ),
                map_panel(INCIDENTS, label="Active incidents"),
            ),
            title="Map layers",
        )

    @app.fragment("/layers/incidents", region=panel)
    def incidents():
        return swap(map_panel(INCIDENTS, label="Active incidents"))

    @app.fragment("/layers/inspections", region=panel)
    def inspections():
        return swap(map_panel(INSPECTIONS, label="Scheduled inspections"))

    return embed_demo(app)
