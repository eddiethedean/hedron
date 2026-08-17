# Maps quickstart

Install `hedron[maps]` (or `hedron-maps>=0.1.0,<0.2`) and return `hedron_maps.Map` from a page.

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
