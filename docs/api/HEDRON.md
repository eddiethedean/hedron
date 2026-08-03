# `Hedron`

**Status:** Accepted

`Hedron` is the batteries-included FastAPI application. It preserves all normal FastAPI behavior while installing Hedron route classes, response handling, lifespan composition, assets, registry, security defaults, and optional development Explorer.

```python
from hedron import Hedron

app = Hedron(
    title="Example",
    security="standard",
    explorer="development",
)
```

## Contract

- Accepts ordinary `FastAPI` constructor options unless explicitly documented otherwise.
- Uses `HedronRoute` and compatible `HedronRouter` instances.
- Component-returning routes render HTML; model-returning routes retain FastAPI JSON behavior.
- User lifespan is composed with Hedron startup and shutdown rather than replaced.
- Explicit `Response` objects pass through unchanged.
- Explorer is absent outside development unless explicitly secured and enabled.

`Hedron` is an ergonomic facade, not a second dependency-injection container, router, task system, or ASGI runtime. Existing applications may use `FastAPI` plus `HedronRouter` without this class.

## Errors

Startup fails for registry collisions, incompatible plugins, invalid component routes, asset conflicts, compiler errors, or unsafe production configuration. Errors identify the responsible subsystem and source.

