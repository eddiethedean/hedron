# What's new in 0.48

**Published in-tree `v0.48.0`** (in-tree cut; tag/PyPI deferred). Owning decisions: D-080 / D-083.
Tracking: [#373](https://github.com/eddiethedean/hedron/issues/373).

PyPI still serves **`hedron` `0.47.0`**. First-run installs should pin `hedron>=0.47.0,<0.48`
from the registry until a later upload; in-tree pins are `hedron>=0.48.0,<0.49`.

## Highlights

- First-class HTMX extension declaration: `Page.htmx_extensions`, `HtmxExtension`, and
  `ExtensionSet` in `hedron-core`.
- Demand-driven pinned local assets (`sse`, `head-support`, `preload`) after HTMX core.
- Unset pages keep the 0.47 `sse` + `head-support` compatibility default; `htmx_extensions=()`
  loads zero extension bytes.
- Typed `SseRegion` / `SseTrigger`. Polling remains the Supported fallback. SSE and preload
  APIs stay experimental.
- GET-only preload authoring on `HtmxLink` (`mousedown` / `mouseover` / `touchstart`).
- Idiomorph / morph swap is **Deferred** and is not a Supported capability.

## Fixed before first PyPI upload

- Head-support admits only local `AssetRef` hrefs, HTML-escapes them, and rejects
  quote/breakout/`..` values. Fragment inject rejects invented `<script>` tags (#374).

This cut does not tag Git, publish a GitHub Release, or upload PyPI.
