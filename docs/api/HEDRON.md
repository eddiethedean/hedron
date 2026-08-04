---
status: shipped
---

# `Hedron`


!!! note "Stability (0.8 freeze)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Accepted · **Shipped in 0.4**

`Hedron` is the batteries-included FastAPI application. It preserves normal FastAPI
behavior while installing Hedron route classes, response handling, lifespan composition,
assets, registry, security defaults, and optional development Explorer.

```python
from hedron import Hedron, Page, Text

app = Hedron(
    title="Example",
    security="standard",
    explorer="off",
    session_secret="replace-me",
    theme="default",
    build_dir=".hedron/build",
    production=None,
)


@app.page("/")
def home() -> Page:
    return Page(Text("ok"), title="Home")
```

## Constructor

| Parameter | Type | Default | Description |
|---|---|---|---|
| `security` | `"development"` \| `"standard"` \| `"strict"` \| `SecurityPolicy` | `"standard"` | Security profile or explicit policy |
| `explorer` | `"off"` \| `"development"` \| `"secured"` \| `None` | `None` | `None` follows policy / `[tool.hedron] explorer`; production forces `development` off |
| `session_secret` | `str` | development default | Required for production; `strict` refuses the built-in default |
| `enable_sessions` | `bool` | `True` | Install Starlette `SessionMiddleware` |
| `explorer_dependencies` | sequence of FastAPI dependencies | `()` | Applied to Explorer when `explorer="secured"` |
| `theme` | `str` \| `None` | `"default"` | Registered theme name for lifespan/build |
| `build_dir` | `str` \| `Path` \| `None` | `None` | Build/manifest directory (else settings / `HEDRON_BUILD_DIR`) |
| `production` | `bool` \| `None` | `None` | `None` uses `HEDRON_ENV`; `True` requires a build manifest and gates runtime compile |

All other keyword arguments are passed to `FastAPI` (`title`, `lifespan`, …).

## Methods

| Method | Description |
|---|---|
| `page(path, **kwargs)` | Register a PAGE route |
| `component(path, **kwargs)` | Register a FRAGMENT/component route |
| `action(path, **kwargs)` | Register an action route (unsafe methods get CSRF) |
| `include_component(descriptor, *, path, **kwargs)` | Expose an `@addressable` descriptor |
| `include_router(...)` | Standard FastAPI router include |

Also see module helpers `mount_hedron_static(app)` and `mount_build_assets(app, build_dir)`.

## Contract

- Uses `HedronRoute` / `HedronRouter` semantics for component returns.
- Component-returning routes render HTML; model-returning routes retain FastAPI JSON behavior.
- User lifespan is composed with Hedron startup/shutdown rather than replaced.
- Explicit `Response` objects pass through unchanged.
- Bundled HTMX is mounted at `/hedron-static/`.
- Explorer is absent when `explorer="off"`. Modes `development` / `secured` require `hedron[dev]`.

`Hedron` is an ergonomic facade, not a second DI container or ASGI runtime. Existing apps
may use `FastAPI` plus `HedronRouter` without this class.

## Errors

| Situation | Behavior |
|---|---|
| Registry / plugin collision | Startup failure with subsystem + source |
| Missing production manifest | `HED-BUILD-0003` (or related); refuse start |
| Default `session_secret` under `strict` | Startup failure |
| Invalid CSRF on unsafe action | HTTP 403 |
| Unauthorized fragment region / OOB | HTTP 403 |

Startup fails for registry collisions, incompatible plugins, invalid component routes,
asset conflicts, compiler errors, missing production manifests, or a default session
secret under `strict`. Errors identify the responsible subsystem and source.

## See also

- [Interaction](INTERACTION.md) · [Security types](SECURITY_TYPES.md) · [Adapters](ADAPTERS.md)
- [Quickstart](../getting-started/quickstart.md)
