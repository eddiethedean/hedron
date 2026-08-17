# HTMX extensions

Phase 0.48 makes official HTMX 2 extensions a **declared** Hedron capability.
Pages name what they need; rendering injects only pinned local assets.

## Declare

Closed public ids: `sse`, `head-support`, `preload`. Morph is Deferred.

```python
from hedron_core.builtins import Page

Page(content, htmx_extensions={"sse", "preload"})
```

- Unset `htmx_extensions` keeps the 0.47 PAGE default (`sse` + `head-support`) and emits
  `HED-EXT-0001`.
- `htmx_extensions=()` or `ExtensionSet.empty()` loads **zero** extension bytes.
- `hx-ext` uses the public id (`sse`, not `htmx-ext-sse`). Writing `hx-ext` in HDJ never
  installs an asset (`HED-JINJA-0030`).

## SSE

Use `SseRegion` / `SseTrigger` with a same-origin `SafeUrl`. Event names are closed tokens.
Keep a `Poll` fallback. Helpers stay on `hedron.experimental`.

## Head-support

When `head-support` is in the compiled plan, PAGE responses may merge admitted `AssetRef`
values. Fragments never invent executable scripts.

## Preload

`HtmxLink(..., preload="mousedown")` is GET-only. It maps to `decide_preload` / `HX-Preloaded`.
Preload never changes authorization or availability.

## Security

Unknown ids, CDN URLs, digest mismatches, and undeclared morph fail closed (`HED-EXT-*`).
Keep `HED-HTMX-0001` / `HED-HTMX-0002`. See [error codes](error-codes.md).
