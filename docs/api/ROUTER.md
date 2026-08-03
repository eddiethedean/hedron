# `HedronRouter` and `HedronRoute`

**Status:** Accepted

```python
from fastapi import Depends
from hedron import HedronRouter

users = HedronRouter(
    prefix="/users",
    dependencies=[Depends(require_user)],
)

@users.page("/")
def users_page() -> UsersPage:
    return UsersPage()
```

`HedronRouter` extends FastAPI `APIRouter` and supports its prefixes, tags, dependencies, responses, and metadata. It adds the canonical `page`, `component`, and `action` registration decorators backed by `HedronRoute`. `Hedron` exposes the same decorators through its root router.

```python
@users.component("/table")
async def user_table() -> UserTable: ...

@users.action("/{user_id}", method="DELETE")
async def delete_user(user_id: str) -> UserTable: ...
```

## Guarantees

- Router dependencies apply to every generated route in the same way as FastAPI routes.
- Names and operation IDs are deterministic and collision checked.
- Internal component resources default to `include_in_schema=False`.
- Component URL generation respects prefixes, mounts, path parameters, and application root paths.
- Component-folder discovery imports only declared router modules and never exposes ordinary components.
- `include_component(descriptor, *, path=...)` is the explicit exposure API for reusable `@addressable` descriptors.

`HedronRoute` is public for advanced integration but most users configure it through the router. Subclassing requires preserving component return handling, registry metadata, OpenAPI behavior, and FastAPI dependency semantics.
