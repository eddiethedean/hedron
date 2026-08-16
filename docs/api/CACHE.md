---
status: shipped
---

# Caching APIs


!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).

**Status:** Shipped

```python
from hedron import cache_component, cache_data


@cache_data(ttl=60, scope="tenant", vary_on=("team_id",))
async def load_summary(team_id: int) -> dict[str, int]:
    ...


@cache_component(ttl=30, scope="private", vary_on=("user_id",))
def user_table(user_id: int):
    ...
```

## `cache_data` / `cache_component`

| Parameter | Type | Description |
|---|---|---|
| `ttl` | `float` \| `None` | Time-to-live seconds (`None` = backend default / no expiry) |
| `scope` | `str` | Logical scope (`public`, `private`, `user`, `tenant`, `session`, …) |
| `version` | `str` | Key version string; bump to invalidate all entries for the callable |
| `tags` | `tuple[str, …]` | Invalidation tags (see `invalidate_tags`) |
| `vary_on` | `tuple[str, …]` | **Required** for sensitive scopes — argument names included in the cache key |

`cache_data` caches typed derived data. `cache_component` caches a prepared component or
rendered result only when the component and security policy permit deterministic reuse.

### Sensitive scopes require `vary_on`

Scopes `private`, `user`, `tenant`, and `session` **must** declare `vary_on` dimensions
(for example `("team_id",)` or `("user_id",)`). Those names must appear as keyword
arguments (or bound parameters) on every call. Omitting `vary_on`, or passing `None` for a
vary key, makes the call **run uncached** (reject + miss) — Hedron does **not** invent
tenant isolation for you.

See [Multi-tenant isolation](../guides/multi-tenant.md).

## Contract

- Keys include function identity, declared public arguments, implementation version, and
  required tenant/user/locale/permission dimensions from `vary_on`.
- Secret arguments are transformed through a non-reversible keyed policy or make the call
  uncacheable; they are never logged or exposed as key text.
- Authenticated results are private unless public safety is explicitly established.
- Concurrent misses support single-flight loading.
- Failures are not cached by default.
- Cancellation of one waiter does not necessarily cancel a shared load.
- Invalidations use explicit tags, versioning, or backend operations; components do not
  infer domain invalidation.

Backends are pluggable. Hedron does not implement a distributed cache service.

`RedisCacheBackend` defaults to prefix `h1:c:` (tag indexes `h1:c:tag:`).
`RedisJobBackend` / `RedisStatusStore` default to `h1:job:`. Sharing one Redis
client is the production archetype, so those prefixes must not nest — including
the legacy cache prefix `h1:`, which the cache constructor rejects. Pass a custom
`prefix=` only when it stays disjoint from the job keyspace.

## Errors

| Condition | Behavior |
|---|---|
| Sensitive scope without `vary_on` | Call runs **uncached** (reject); no shared entry |
| Sensitive scope missing / `None` vary values | Call runs **uncached** (reject) |
| Uncacheable arguments / secrets | Call runs uncached or raises per policy |
| Backend failure | Propagates; not stored as a successful entry |
| `public` scope with request/user kwargs | Rejected as uncacheable |

## See also

[State](STATE.md) · authenticated caching note on `request.state.hedron_authenticated` ·
[Multi-tenant isolation](../guides/multi-tenant.md) · Autodoc `cache_data` / `cache_component`
