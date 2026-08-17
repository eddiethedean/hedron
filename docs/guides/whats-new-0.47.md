# What's new in 0.47

**Published in-tree `v0.47.0`** (in-tree cut; tag/PyPI deferred). Owning decisions: D-078 / D-082.
Tracking: [#350](https://github.com/eddiethedean/hedron/issues/350).

PyPI still serves **`hedron` `0.46.0`**. First-run installs should pin `hedron>=0.46.0,<0.47`
from the registry until a later upload; in-tree pins are `hedron>=0.47.0,<0.48`.

## Highlights

- Independent Beta **`hedron-maps` `0.1.0`**: `MapSpec` / `MapPlan` / `compile_map`,
  `hedron_maps.Map`, OSM preset, custom/offline sources, `hedron-map` + MapLibre 5.6.1
  strict-CSP, and `MapInteraction`.
- Core `hedron.Map` and charts MapLibre/Folium/PyDeck stay explicit and optional.
- `hedron_maps.GeoJSONLayer` is the typed overlay; `hedron_core.GeoJSONLayer` is the sanitizer.

This cut does not tag Git, publish a GitHub Release, or upload PyPI.

## Fixed before first PyPI upload

- Custom OSM `tile_url`, `Map(tiles=)`, and MapStyle `data`/`urls` honor exact-origin policy (#351–#353).
- Generated DataWorkspace lists page/sort/filter; policy hooks receive identity and deny closed (#354, #355).
- `hedron-mcp` **0.2.1** keeps per-tool authorize instead of overwriting the projection hook (#356).
- `MapInteraction` POSTs feature events to the registered command path (#357).
