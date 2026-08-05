---
status: shipped
---

# Addressable component APIs

!!! note "Stability (0.11 train)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).

**Status:** Accepted · **Shipped**

For application-local resources, `@router.component(...)` declares and registers the
factory. Reusable packages may define a resource with `@addressable` and expose it later.

## App-local component route

```python
from fastapi import Depends
from hedron import HedronRouter, Text

users = HedronRouter(prefix="/users")


@users.component("/table", dependencies=[Depends(require_user)])
async def user_table() -> Text:
    return Text("rows")
```

### `@router.component` parameters

| Parameter | Description |
|---|---|
| `path` | Fragment route path |
| `methods` | Default `GET`; include `POST` for mutations |
| `fragment_regions` | Allowlisted `FragmentRegion` targets |
| `dependencies` / `tags` / `name` | FastAPI route options |

## Package-level `@addressable`

```python
from hedron_core import addressable
from hedron import Text

@addressable
async def user_table() -> Text:
    return Text("rows")

users.include_component(user_table, path="/table")
```

| API | Role |
|---|---|
| `@addressable(...)` | Creates a descriptor; **not** HTTP-reachable alone |
| `router.include_component(descriptor, path=..., dependencies=...)` | Explicit exposure |

## Errors

| Situation | Behavior |
|---|---|
| HX-Target outside `fragment_regions` | HTTP 403 |
| Double registration / identity collision | Startup failure |
| Calling a package descriptor without `include_component` | No route |

## See also

- [Router](ROUTER.md) · [Reference app walkthrough](../examples/reference-app.md)
