# What's new in 0.47

**Published `v0.47.0`** (Git tag, GitHub Release, and PyPI). Owning decisions: D-078 / D-082.
Tracking: [#350](https://github.com/eddiethedean/hedron/issues/350).

PyPI serves **`hedron` `0.47.0`**. First-run installs until the 0.48 upload should pin
`hedron>=0.47.0,<0.48`; the living in-tree tip is `hedron>=0.49.0,<0.50`.

## Highlights

- Independent Beta **`hedron-maps` `0.1.0`**: `MapSpec` / `MapPlan` / `compile_map`,
  `hedron_maps.Map`, OSM preset, custom/offline sources, `hedron-map` + MapLibre 5.6.1
  strict-CSP, and `MapInteraction`.
- Core `hedron.Map` and charts MapLibre/Folium/PyDeck stay explicit and optional.
- `hedron_maps.GeoJSONLayer` is the typed overlay; `hedron_core.GeoJSONLayer` is the sanitizer.

Git tag `v0.47.0`, GitHub Release, and PyPI `hedron` `0.47.0`.

## Fixed before first PyPI upload

- Custom OSM `tile_url`, `Map(tiles=)`, and MapStyle `data`/`urls` honor exact-origin policy (#351–#353).
- Generated DataWorkspace lists page/sort/filter; policy hooks receive identity and deny closed (#354, #355).
- `hedron-mcp` **0.2.1** keeps per-tool authorize instead of overwriting the projection hook (#356).
- `MapInteraction` POSTs feature events to the registered command path (#357).
