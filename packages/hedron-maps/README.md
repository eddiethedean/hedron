# hedron-maps

First-class maps, offline geospatial presentation, and `MapInteraction` for Hedron.

**Package maturity:** Beta · **Package version:** `0.1.4` · requires
`hedron-core>=1.0.0,<2.0`

Install with the 0.51 train extra `hedron[maps]` or independently:

```bash
pip install "hedron-maps>=0.1.4,<0.2"
```

```python
from hedron_maps import Map

Map(center=(37.7749, -122.4194), zoom=11, title="Bay Area", description="OSM raster map")
```

The default is `OpenStreetMap.standard()` on `hedron_maps.Map` only. Core `hedron.Map`
keeps no OSM default. Enhanced rendering uses a pinned MapLibre GL JS **5.6.1** strict-CSP
build (not the experimental charts 4.5.0 pin). Semantic `.hedron-map-alternative` tables
remain when JavaScript, WebGL, workers, or tiles are absent.

See [Maps API](https://hedron.readthedocs.io/en/latest/api/MAPS/).
