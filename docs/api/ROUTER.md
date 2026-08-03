# `HedronRouter` and `HedronRoute`

**Status:** Proposed

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

`HedronRouter` extends FastAPI `APIRouter` and supports its prefixes, tags, dependencies, responses, and metadata. It adds `page`, `component`, and `action` registration conveniences backed by `HedronRoute`.

## Guarantees

- Router dependencies apply to every generated route in the same way as FastAPI routes.
- Names and operation IDs are deterministic and collision checked.
- Internal component resources default to `include_in_schema=False`.
- Component URL generation respects prefixes, mounts, path parameters, and application root paths.
- Component-folder discovery imports only declared router modules and never exposes ordinary components.

`HedronRoute` is public for advanced integration but most users configure it through the router. Subclassing requires preserving component return handling, registry metadata, OpenAPI behavior, and FastAPI dependency semantics.

