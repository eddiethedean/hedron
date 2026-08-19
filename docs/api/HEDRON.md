---
status: shipped
---

# `Hedron`


!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Accepted · **Shipped** (introduced in 0.4; current train **0.51.x**)

`Hedron` is the batteries-included FastAPI application. It preserves normal FastAPI
behavior while installing Hedron route classes, response handling, lifespan composition,
assets, registry, security defaults, and optional development Explorer.

```python
from hedron import Hedron, Page, Text

app = Hedron(
    title="Example",
    security="standard",
    explorer="off",
    session_secret="replace-in-production",
    theme="default",
    default_styles=True,
    build_dir=".hedron/build",
    production=None,
)


@app.page("/")
def home() -> Page:
    return Page(Text("ok"), title="Home")
```

## Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `security` | `"development"` \| `"standard"` \| `"strict"` \| `SecurityPolicy` | `"standard"` | Security profile or explicit policy |
| `explorer` | `"off"` \| `"development"` \| `"secured"` \| `None` | `None` | `None` follows policy / `[tool.hedron] explorer`; production forces `development` off |
| `session_secret` | `str` \| `None` | development default | Required when `enable_sessions=True` (`None` is refused). Production rejects missing/weak values; `strict` refuses the built-in default |
| `enable_sessions` | `bool` | `True` | Install Starlette `SessionMiddleware` |
| `explorer_dependencies` | sequence of FastAPI dependencies | `()` | Applied to Explorer when `explorer="secured"` |
| `theme` | `str` \| `None` | `"default"` | Registered theme name for lifespan/build |
| `default_styles` | `bool` | `True` | Include Hedron's responsive baseline presentation; set `False` for a fully custom canvas |
| `build_dir` | `str` \| `Path` \| `None` | `None` | Build/manifest directory (else settings / `HEDRON_BUILD_DIR`) |
| `production` | `bool` \| `None` | `None` | `None` uses `HEDRON_ENV`; `True` requires a build manifest and gates runtime compile |

All other keyword arguments are passed to `FastAPI` (`title`, `lifespan`, `middleware`,
`docs_url`, OpenAPI options, …). Hedron does **not** wrap a second ASGI runtime.

## Hedron vs `FastAPI()`

| Topic | Behavior |
|---|---|
| Unrecognized kwargs | Forwarded to `FastAPI` |
| Lifespan | Your lifespan is **composed** with Hedron startup/shutdown, not replaced |
| Middleware | You may add Starlette/FastAPI middleware as usual |
| OpenAPI | `include_in_schema` defaults: `True` for page/action, `False` for component |
| `HEDRON_SESSION_SECRET` | **Convention only** — Hedron never reads the env var. Pass `session_secret=` |
| `HEDRON_ENV` / `production=` | Production mode; `HEDRON_BUILD_DIR` is loaded for the build manifest |
| Existing app | Use `HedronRouter` + `mount_hedron_static` instead of this class |

See [Secrets, sessions, and workers](../guides/secrets-and-workers.md) and
[Plain FastAPI](../guides/plain-fastapi.md).

## Methods

Decorator kwargs are the same as on `HedronRouter` (see [Router](ROUTER.md)). Common
parameters:

| Parameter | Applies to | Type | Default | Description |
|---|---|---|---|---|
| `path` | all | `str` | required | Route path (FastAPI pattern) |
| `methods` | `page`, `component` | sequence of HTTP methods | `["GET"]` | Allowed verbs; unsafe methods enable CSRF when configured |
| `method` | `action` only | `str` | `"POST"` | Primary verb when `methods` is omitted |
| `name` | all | `str \| None` | function name | FastAPI route name |
| `include_in_schema` | all | `bool` | `True` for page/action; `False` for component | OpenAPI inclusion |
| `dependencies` | all | FastAPI `Depends` sequence | `None` | Route dependencies (auth gates, etc.) |
| `tags` | all | list | `None` | OpenAPI tags |
| `fragment_regions` | `page`, `component`, `action` | sequence of `FragmentRegion` | `None` | HTMX `HX-Target` allowlist for this route |
| `**kwargs` | all | FastAPI route options | — | Passed through to `add_api_route` (for example `response_class`) |

| Method | Description |
|---|---|
| `page(path, **kwargs)` | Register a PAGE route (navigation HTML; fragment when `HX-Request`) |
| `refreshable(path, **kwargs)` | Register a GET fragment view; returns a `FragmentHandle` |
| `command(path, **kwargs)` | Register a CSRF-backed mutation; returns an `ActionHandle` |
| `component(path, **kwargs)` | Register a FRAGMENT route; use `methods=["POST"]` for HTMX form fragments with `fragment_regions` |
| `action(path, **kwargs)` | Register an action route (CSRF on unsafe methods). Prefer `@command` for new forms; see [ACTION](ACTION.md) |
| `region(id, selector=None, description="")` | Declare a `FragmentRegion` (default selector `#{id}`) for `RefreshButton.for_region` / allowlists |
| `fragment(path, region=..., regions=..., **kwargs)` | Alias of `component` that merges `region` / `regions` into the allowlist |
| `include_component(descriptor, *, path, **kwargs)` | Expose an `@addressable` descriptor |
| `include_feature(bundle, *, capabilities=None)` | Include one `FeatureBundle` / `FeatureProvider` before registry/catalog seal |
| `include_router(...)` | Standard FastAPI router include |

Golden-path HTMX uses `@app.refreshable` and `@app.command` (see
[Refreshable views](REFRESHABLE_VIEWS.md) and
[HTMX interactions](../guides/htmx-interactions.md)). `page` / `component` / `action`
plus `fragment_regions` remain the lower-level allowlist API.

```python
from hedron import Hedron, Page, Stack, Text, html, refresh

app = Hedron(title="Demo", security="standard", explorer="off", session_secret="replace-in-production")


@app.refreshable("/status")
def status():
    return html.div(Text("ok"), role="status")


@app.command("/notes")
def save():
    return refresh(status)


@app.page("/")
def home() -> Page:
    return Page(Stack(status(), status.refresh_button("Refresh"), save.form()), title="Home")
```

Also see module helpers `mount_hedron_static(app)` and `mount_build_assets(app, build_dir)`.

Choosing between `@action` and `@component(..., methods=["POST"])`:
see [Mutations](../guides/mutations.md).

## Returns

| Method / helper | Returns | Notes |
|---|---|---|
| `@app.page` / `@app.component` / `@app.action` decorators | The decorated callable (registered on the app) | Handler return values are rendered by `HedronRoute` |
| Page handler | `Page`, `InteractionResult`, model, or Starlette `Response` | PAGE HTML for navigation; FRAGMENT when `HX-Request` + authorized target |
| Component / fragment handler | Component tree, `InteractionResult`, or `Response` | FRAGMENT mode by default |
| Action handler | Component, `InteractionResult`, redirect helper, or `Response` | CSRF on unsafe methods when the profile enables it |
| `app.region(...)` | `FragmentRegion` | Default selector `#{id}` |
| `mount_hedron_static(app)` / `mount_build_assets(...)` | `None` | Mutates the ASGI app mounts |

Rendered HTML responses use Hedron response classes (`PageResponse` / `FragmentResponse`)
unless the handler returns an explicit Starlette/FastAPI `Response`.

## Contract

- Uses `HedronRoute` / `HedronRouter` semantics for component returns.
- Component-returning routes render HTML; model-returning routes retain FastAPI JSON behavior.
- User lifespan is composed with Hedron startup/shutdown rather than replaced.
- Explicit `Response` objects pass through unchanged.
- Bundled HTMX is mounted at `/hedron-static/`.
- Full pages include Hedron's bundled default stylesheet unless `default_styles=False`;
  fragments do not repeat document-level assets.
- Explorer is absent when `explorer="off"`. Modes `development` / `secured` require `hedron[dev]`.

`Hedron` is an ergonomic facade, not a second DI container or ASGI runtime. Existing apps
may use `FastAPI` plus `HedronRouter` without this class.

## Errors

| Situation | Behavior |
|---|---|
| Registry / plugin collision | Startup failure with subsystem + source |
| Missing production manifest | `HED-BUILD-0003` (or related); refuse start |
| Default `session_secret` under `strict` | Startup failure |
| `session_secret=None` with sessions enabled | Startup failure |
| Invalid CSRF on unsafe action | HTTP 403 |
| Unauthorized fragment region / OOB | HTTP 403 |

Startup fails for registry collisions, incompatible plugins, invalid component routes,
asset conflicts, compiler errors, missing production manifests, a default session
secret under `strict`, or `session_secret=None` when sessions are enabled. Errors identify
the responsible subsystem and source.

## See also

- [Interaction](INTERACTION.md) · [Security types](SECURITY_TYPES.md) · [Adapters](ADAPTERS.md)
- [Quickstart](../getting-started/quickstart.md)
- Autodoc: [AUTODOC.md](AUTODOC.md)
