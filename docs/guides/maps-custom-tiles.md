# Custom XYZ, TileJSON, and vector tiles

```python
from hedron_maps import Map, MapPolicy, RasterTiles, TileJSON, VectorTiles

policy = MapPolicy(allowed_origins={"https://maps.example.com"})

xyz = Map(
    title="XYZ",
    description="Exact-origin raster",
    basemap=RasterTiles(
        url="https://maps.example.com/{z}/{x}/{y}.png",
        attribution="© Example Maps",
    ),
    policy=policy,
)
```

Templates require `{z}{x}{y}`. Scale/subdomain placeholders are opt-in fields, not
arbitrary interpolation. Credentials, protocol-relative URLs, and HTTP remotes fail
closed. TileJSON and `VectorTiles` close every sprite/glyph/source origin against
`MapPolicy.allowed_origins`.
