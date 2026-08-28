# What's new in 0.47

!!! note "Historical release note"

    This page records the 0.x release named in its title. For current installation,
    support, and 1.0 candidate status, use [Current release and support](current-release.md).
    Keep the historical pins below only when maintaining that release line.

**Published `v0.47.0`** (Git tag, GitHub Release, and PyPI). Owning decisions: D-078 / D-082.
Tracking: [#350](https://github.com/eddiethedean/hedron/issues/350).
For new apps, use `hedron>=0.58.0,<0.60`; see [What’s new in 0.51](whats-new-0.51.md).

## Highlights

- Independent Beta **`hedron-maps` `0.1.0`**: `MapSpec` / `MapPlan` / `compile_map`,
  `hedron_maps.Map`, OSM preset, custom/offline sources, `hedron-map` + MapLibre 5.6.1
  strict-CSP, and `MapInteraction`.
- Core `hedron.Map` and charts MapLibre/Folium/PyDeck stay explicit and optional.
- `hedron_maps.GeoJSONLayer` is the presentation overlay; `hedron_core.GeoJSONLayer` is the sanitizer.

Git tag `v0.47.0`, GitHub Release, and PyPI `hedron` `0.47.0`.

## Fixed before first PyPI upload

- Custom OSM `tile_url`, `Map(tiles=)`, and MapStyle `data`/`urls` honor exact-origin policy (#351–#353).
- Generated DataWorkspace lists page/sort/filter; policy hooks receive identity and deny closed (#354, #355).
- `hedron-mcp` **0.2.1** keeps per-tool authorize instead of overwriting the projection hook (#356).
- `MapInteraction` POSTs feature events to the registered command path (#357).
