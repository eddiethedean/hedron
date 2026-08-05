---
status: shipped
---

# `Action`

!!! note "Stability (0.11 train)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).

**Status:** Accepted · **Shipped**

An action is a typed server operation bound to UI controls and normal FastAPI request
processing.

```python
from hedron import HedronRouter, Text

users = HedronRouter(prefix="/users")


@users.action("/{user_id}", method="DELETE")
async def delete_user(user_id: int) -> Text:
    await service.delete(user_id)
    return Text("deleted")
```

## Decorator

`@router.action(path, *, method="POST", methods=None, name=None, dependencies=None, tags=None, **fastapi_kwargs)`

| Parameter | Description |
|---|---|
| `path` | Route path relative to the router prefix |
| `method` / `methods` | HTTP verbs; unsafe methods get CSRF when enabled |
| `dependencies` | FastAPI dependencies (auth gates, etc.) |
| Other kwargs | Passed to FastAPI `add_api_route` |

Returns are rendered as fragments by default.

| Return type | Behavior |
|---|---|
| `NodeLike` / built-in component | Fragment HTML |
| `InteractionResult` | Fragment HTML + validated HTMX metadata |
| `Page` | Page document when the route/render mode expects a page |
| FastAPI `Response` | Passed through |

Prefer `InteractionResult` when you need typed HTMX metadata. Note: `fragment_regions`
is supported on `@component` / `@page`, not on `@action` today—use
`@component(..., methods=["POST"], fragment_regions=...)` when you need an allowlisted
HTMX target for a mutation ([forms guide](../guides/forms-and-actions.md)).

## Contract

- Method, route, input contract, dependencies, and return behavior are explicit.
- Hedron may infer URL, target, swap, CSRF mechanics, loading state, and validation-fragment handling from registration.
- It never infers permission, destructive meaning, confirmation policy, or persistence.
- GET actions cannot mutate by contract.
- Unsafe cookie-authenticated actions validate CSRF (`X-CSRF-Token` or `csrf_token` form field vs `hedron_csrf` cookie).

## Errors

| Situation | Behavior |
|---|---|
| Missing/invalid CSRF | HTTP 403 |
| Unauthorized application dependency | Your dependency’s HTTP error |
| Invalid local redirect | Rejected by security policy |

## See also

- [Router](ROUTER.md) · [Interaction](INTERACTION.md) · [Security](../guides/security.md)
