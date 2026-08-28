# Maps quickstart

For the coordinated 1.0 artifacts, install `hedron-maps>=0.1.4,<0.2` and return
`hedron_maps.Map` from a page. Public PyPI applications should use
`hedron[maps]>=0.66.2,<0.67` until the 1.0 train is published.

```python
from hedron_maps import Map

def page():
    return Map(
        center=(37.7749, -122.4194),
        zoom=11,
        title="Bay Area",
        description="Replaceable OpenStreetMap raster map",
    )
```

The server always renders `.hedron-map-alternative` (a feature/marker table). The
`hedron-map` element upgrades from a compiled `MapPlan` when MapLibre is available.
The OSM preset is not an SLA.

Core `from hedron import Map` is unchanged and has no OSM default.

## Try markers and filtering (simulated)

This demo renders the real `hedron_maps.Map` plan and its semantic feature table. The docs
simulation performs HTMX-style fragment swaps, but deliberately makes no live tile requests.

=== "Demo"

    Filter package-native map markers and inspect the accessible fallback table. Docs simulation; no live tile requests.

    <!-- hedron-sim:maps-markers -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
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
    ```
