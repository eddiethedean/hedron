---
status: shipped
---

# Rendering API


!!! note "Stability (0.8 freeze)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Accepted

The public core rendering boundary is intentionally small:

```python
from hedron_core import RenderContext, RenderMode, RenderResult, render

context = RenderContext.standalone(locale="en", theme="default")
result = render(component, context=context, mode=RenderMode.FRAGMENT)
html_text = result.html
```

## Types

- `NodeLike`: the public recursive typing alias for accepted render inputs and component returns, including a component, native HTML node, string, supported sequence, or `None`.
- `ComponentNode`: an opaque protocol implemented by public component and native-node values; objects exposing `__hedron_node__()` are accepted by `render`. Concrete normalized serializer nodes stay private.
- `RenderMode`: `PAGE` or `FRAGMENT` in the phase 0.1 contract shipping in `v0.1.0`.
- `RenderContext`: immutable framework-neutral rendering context. `RenderContext.standalone(*, locale="en", theme=None)` creates the supported direct-rendering context; framework adapters derive request contexts without storing a raw request, session, or dependency object in it.
- `RenderResult`: immutable result with `html: str`, `mode: RenderMode`, `assets`, approved `headers`, `identity_map`, `diagnostics`, and an optional redacted `trace`. Collection fields are immutable snapshots.

`render(value, *, context=None, mode=RenderMode.FRAGMENT) -> RenderResult` is the advanced framework-neutral entry point. Ordinary application code returns components and lets its framework adapter call `render`. Cycle detection tracks component instance identity, so nested same-type composition (for example `Stack(Stack(...))`) is valid while true self-recursion fails with `HED-RENDER-0012`.

Passing `context=None` is equivalent to a default standalone context. Output is Unicode HTML; HTTP adapters alone perform the configured encoding. A result contains no raw secret, request, session, or dependency object. Header metadata is produced only by registered page/fragment policies and is revalidated by the framework adapter.

## Stability boundary

Concrete internal text, element, fragment, and boundary node classes are private in 0.x. Applications compose public components and `hedron.html` primitives rather than constructing serializer nodes directly. The HTML serializer is not a public independent API; it consumes normalized nodes through the rendering engine.

Strings are text and are always escaped. Raw markup requires `TrustedHtml` and an explicit trusted-HTML primitive. Iterators with hidden I/O are not accepted as node sequences.
