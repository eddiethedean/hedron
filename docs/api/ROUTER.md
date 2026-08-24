---
status: shipped
---

# `HedronRouter` and `HedronRoute`


!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Accepted · **Shipped** (introduced in 0.4; current train **0.63.x**)

```python
from fastapi import Depends
from hedron import HedronRouter, Page, Text

users = HedronRouter(
    prefix="/users",
    dependencies=[Depends(require_user)],
)


@users.page("/")
def users_page() -> Page:
    return Page(Text("Users"), title="Users")
```

`HedronRouter` extends FastAPI `APIRouter` and supports prefixes, tags, dependencies,
responses, and metadata. It adds `page`, `refreshable`, `command`, `component`, and
`action` registration decorators backed by `HedronRoute`. `Hedron` exposes the same
decorators on its root router.

```python
@users.refreshable("/table")
def user_table():
    return Text("Users")


@users.command("/{user_id}")
def delete_user(user_id: str):
    ...
```

Declare the fragment regions a page or component route is authorized to update:

```python
from hedron import FragmentRegion, InteractionResult

USERS_TABLE = FragmentRegion(id="users-table", selector="#users-table")


@users.component("/table", fragment_regions=(USERS_TABLE,))
async def user_table() -> InteractionResult: ...
```

An `HX-Target` outside the route allowlist receives `403`. Route declarations override a
conflicting `InteractionResult.policy.declared_regions` value.

## Decorators

| Decorator | Typical return | Notes |
|---|---|---|
| `@router.page(path, **kwargs)` | `Page` / document | PAGE mode for navigation; fragment for `HX-Request`; accepts `fragment_regions` |
| `@router.refreshable(path, **kwargs)` | Fragment / `FragmentHandle` | Golden-path GET view; use `handle.refresh_button(...)` |
| `@router.command(path, **kwargs)` | `ActionHandle` | Golden-path CSRF mutation; use `handle.form()` / `handle.button(...)` |
| `@router.component(path, **kwargs)` | Component / fragment | Lower-level FRAGMENT mode; accepts `fragment_regions` |
| `@router.action(path, method=..., **kwargs)` | Component or redirect | Lower-level CSRF action; prefer `@command` for new forms |

On the flagship `Hedron` app (root router), prefer `@app.refreshable` and `@app.command`.
`app.region(...)` plus `@app.fragment(...)` remain available for explicit HTMX allowlists.

`HedronRouter` exposes the same decorators. See [Hedron](HEDRON.md) and
[Refreshable views](REFRESHABLE_VIEWS.md).

Keyword arguments follow FastAPI route options (`name`, `dependencies`,
`include_in_schema`, `methods`, `tags`, …).

## `include_component`

```python
from hedron_core import addressable

@addressable(methods=("GET", "POST"))
def piece() -> Text:
    return Text("ok")

router.include_component(piece, path="/piece", dependencies=[Depends(gate)])
```

CSRF applies when any declared method is unsafe.

## Guarantees

- Router dependencies apply to every generated route like FastAPI.
- Names and operation IDs are deterministic and collision checked.
- Internal component resources default to `include_in_schema=False`.
- Component URL generation respects prefixes, mounts, path parameters, and root paths.
- `include_component` is the explicit exposure API for reusable `@addressable` descriptors.

`HedronRoute` is public for advanced integration. It converts `HTML(...)` and component
returns before FastAPI serializes them, and issues CSRF cookies once per safe GET when
CSRF is enabled.

## Parameters

Decorator kwargs match FastAPI route options plus Hedron allowlists. See the parameter
table on [Hedron](HEDRON.md#methods) (`path`, `methods` / `method`, `name`,
`dependencies`, `tags`, `fragment_regions`, `include_in_schema`, …).

## Returns

| API | Returns |
|---|---|
| `@router.page` / `@router.component` / `@router.action` | The decorated callable (route registered) |
| Handler body | `Page`, component tree, `InteractionResult`, model JSON, or explicit `Response` |
| `include_component(descriptor, path=...)` | Registered routes for the addressable descriptor |
| Rendered HTMX/HTML | Hedron HTML response classes unless an explicit `Response` is returned |

## Errors

| Situation | Behavior |
|---|---|
| HX-Target outside allowlist | HTTP 403 |
| CSRF failure on unsafe method | HTTP 403 |
| Operation ID / name collision | Startup failure |
| Missing static mount for PAGE HTMX | Browser 404 on `/hedron-static/...` |

Plain FastAPI apps should call `mount_hedron_static(app)` so PAGE responses that inject
`/hedron-static/htmx.min.js` resolve. See [Plain FastAPI](../guides/plain-fastapi.md).

## See also

- [Hedron](HEDRON.md) · [Interaction](INTERACTION.md) · [Addressable](ADDRESSABLE.md)
- Autodoc: [AUTODOC.md](AUTODOC.md)
