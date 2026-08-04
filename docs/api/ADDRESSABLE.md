---
status: shipped
---

# Addressable component APIs


!!! note "Stability (0.8 compatibility baseline)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Accepted

For application-local resources, `@router.component(...)` is the canonical API and both declares and registers the addressable factory.

```python
from fastapi import Depends
from hedron import HedronRouter

users = HedronRouter(prefix="/users")

@users.component("/table", dependencies=[Depends(require_user)])
async def user_table(team_id: int) -> UserTable:
    return UserTable(rows=await load_users(team_id))
```

Reusable packages may define a resource without exposing a route:

```python
from hedron_core import addressable

@addressable
async def user_table(team_id: int) -> UserTable:
    ...

users.include_component(user_table, path="/table")
```

`@addressable` creates a reusable typed resource descriptor. It is not reachable over HTTP until an application explicitly calls `include_component` or registers it through equivalent router configuration.

## Contract

- The factory signature defines public route inputs and FastAPI dependencies.
- The return annotation defines the component response contract.
- Declaration and HTTP exposure are explicit; app-local decorator registration performs both intentionally.
- Defaults include safe methods, private caching under authentication, hidden internal schema status, and stable route identity.
- Factories may be synchronous or asynchronous.

Component references accept only declared public inputs. They resolve URLs and HTMX mechanics through the registry and never serialize dependency objects, secrets, or authorization decisions.

Configuration may declare route path/name, methods, caching, lazy fallback, timeout policy, tags, and schema visibility. Public exposure, mutation, or relaxed caching requires explicit configuration.
