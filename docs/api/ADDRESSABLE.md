# `addressable`

**Status:** Proposed

`addressable` registers a component-producing factory as an HTTP resource.

```python
from fastapi import Depends
from hedron import addressable

@addressable(dependencies=[Depends(require_user)])
async def user_table(team_id: int) -> UserTable:
    return UserTable(rows=await load_users(team_id))
```

## Contract

- The factory signature defines public route inputs and FastAPI dependencies.
- The return annotation defines the component response contract.
- Registration is explicit and may be attached to a `HedronRouter`.
- Defaults include safe methods, private caching under authentication, hidden internal schema status, and stable route identity.
- Factories may be synchronous or asynchronous.

Component references accept only declared public inputs. They resolve URLs and HTMX mechanics through the registry and never serialize dependency objects, secrets, or authorization decisions.

Configuration may declare route path/name, methods, caching, lazy fallback, timeout policy, tags, and schema visibility. Public exposure, mutation, or relaxed caching requires explicit configuration.

