---
status: shipped
---

# Caching APIs


!!! note "Stability (0.8 freeze)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Accepted

```python
@cache_data(ttl=60, scope="tenant")
async def load_summary(team_id: int) -> Summary:
    ...

@cache_component(ttl=30, scope="private")
def user_table(team_id: int) -> UserTable:
    ...
```

`cache_data` caches typed derived data. `cache_component` caches a prepared component or rendered result only when the component and security policy permit deterministic reuse.

## Contract

- Keys include function identity, declared public arguments, implementation version, and required tenant/user/locale/permission dimensions.
- Secret arguments are transformed through a non-reversible keyed policy or make the call uncacheable; they are never logged or exposed as key text.
- Authenticated results are private unless public safety is explicitly established.
- Concurrent misses support single-flight loading.
- Failures are not cached by default.
- Cancellation of one waiter does not necessarily cancel a shared load.
- Invalidations use explicit tags, versioning, or backend operations; components do not infer domain invalidation.

Backends are pluggable. Hedron does not implement a distributed cache service. Explorer reports hit, miss, wait, age, scope, size, and invalidation metadata without displaying sensitive keys or values.

