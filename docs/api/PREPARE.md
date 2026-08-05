---
status: shipped
---

# Component `prepare()` lifecycle

!!! note "Stability"

    Classifications live in [STABILITY.md](STABILITY.md). `prepare()` is **Supported**
    (beta API level) on the 0.13 train. Opt out by omitting `prepare` on components —
    sync `render()` semantics are unchanged.

**Status:** Shipped in `0.13.0`

Optional async (or sync) work **before** sync `render()` for components that define
`prepare(self, ctx: PrepareContext)`. Request-owned: deadlines, disconnect cancel,
partial-failure policy, and a per-request cache.

## Imports

```python
from hedron_core.prepare import PrepareContext, PartialFailurePolicy
from hedron_core.component import Component
from hedron_core.models import Props
```

## `PrepareContext`

| Member | Role |
|---|---|
| `deadline` | Optional monotonic deadline |
| `cancel_event` | Optional `asyncio.Event` for disconnect |
| `partial_failure` | `PartialFailurePolicy.FAIL_FAST` or `CONTINUE` |
| `cache` | Request-local dict for memoization |
| `remaining()` / `is_cancelled()` / `check()` | Budget helpers; `check()` raises `HED-PREPARE-0001` |
| `cached(key, factory)` | Async memoize through `cache` |

## Example

```python
class BannerProps(Props):
    pass


class PreparedBanner(Component[BannerProps]):
    props_type = BannerProps

    async def prepare(self, ctx: PrepareContext) -> None:
        ctx.check()
        self._label = await ctx.cached("label", lambda: "ready")

    def render(self) -> object:
        from hedron_core import Text

        return Text(getattr(self, "_label", "…"))
```

## Errors

| Code | When |
|---|---|
| `HED-PREPARE-0001` | Prepare cancelled by disconnect or deadline |

## Related

- [What’s new in 0.13](../guides/whats-new-0.13.md)
- Autodoc: [AUTODOC.md](AUTODOC.md#prepare-lifecycle-013)
- Live sample: [`examples/live-interaction`](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction)
