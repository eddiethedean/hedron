# Map accessibility

Every non-decorative map needs a title and useful description. The semantic alternative
is `.hedron-map-alternative` (feature/marker table and ordinary links/buttons).

Keyboard: the canvas host is focusable; Escape leaves; Tab is not trapped. Gestures are
cooperative. Selection is not color-only. Reduced-motion disables animation. Forced-colors
and dark mode retokenize `--hedron-map-*`.

This is a scoped authoring contract. It does **not** close `SR-021` or claim spatial
canvas equivalence for assistive technology.

## Try the semantic alternative (simulated)

Switch layers to verify that the ordinary HTML feature table changes with the map plan.
The docs simulation does not load MapLibre or request tiles.

=== "Demo"

    Swap typed GeoJSON layers while keeping their feature names and coordinates available as HTML. Docs simulation; no live tile requests.

    <!-- hedron-sim:maps-layers -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
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


    @app.fragment("/layers/incidents", region=panel)
    def incidents():
        return swap(map_panel(INCIDENTS, label="Active incidents"))


    @app.fragment("/layers/inspections", region=panel)
    def inspections():
        return swap(map_panel(INSPECTIONS, label="Scheduled inspections"))
    ```
