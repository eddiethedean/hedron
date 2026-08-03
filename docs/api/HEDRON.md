# `Hedron`

**Status:** Accepted

`Hedron` is the batteries-included FastAPI application. It preserves all normal FastAPI behavior while installing Hedron route classes, response handling, lifespan composition, assets, registry, security defaults, and optional development Explorer.

```python
from hedron import Hedron

app = Hedron(
    title="Example",
    security="standard",
    explorer="development",
    session_secret="replace-me",
)
```

## Constructor notes

- `security`: `"development"`, `"standard"`, or `"strict"` (or a `SecurityPolicy`).
- `explorer`: `"off"` (default), `"development"` (mounts Explorer even under standard security), or `"secured"` (mounts Explorer behind authentication).
- `session_secret`: required for production. The built-in development default emits a warning; `security="strict"` refuses that default.
- `explorer_dependencies`: optional FastAPI dependencies applied to Explorer routes (used with `explorer="secured"`).

## Contract

- Accepts ordinary `FastAPI` constructor options unless explicitly documented otherwise.
- Uses `HedronRoute` and compatible `HedronRouter` instances.
- Component-returning routes render HTML; model-returning routes retain FastAPI JSON behavior.
- User lifespan is composed with Hedron startup and shutdown rather than replaced.
- Explicit `Response` objects pass through unchanged.
- Bundled HTMX is mounted at `/hedron-static/` (also available via `mount_hedron_static(app)` for plain FastAPI apps).
- Explorer is absent when `explorer="off"`. Explicit `development` / `secured` modes mount the preview from `hedron[dev]`.

`Hedron` is an ergonomic facade, not a second dependency-injection container, router, task system, or ASGI runtime. Existing applications may use `FastAPI` plus `HedronRouter` without this class.

## Errors

Startup fails for registry collisions, incompatible plugins, invalid component routes, asset conflicts, compiler errors, or unsafe production configuration (including a default session secret under `strict`). Errors identify the responsible subsystem and source.
