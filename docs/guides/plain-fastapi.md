# Plain FastAPI + HedronRouter

Use Hedron’s routing and HTML responses without the `Hedron()` facade when you
already own a `FastAPI` app.

```python
from fastapi import FastAPI

from hedron import HedronRouter, Page, Text, mount_hedron_static
from hedron.security import SecurityPolicy

api = FastAPI(title="Existing API")
api.state.hedron_security = SecurityPolicy.from_name("standard")
mount_hedron_static(api)

ui = HedronRouter(prefix="/ui")


@ui.page("/")
def home() -> Page:
    return Page(Text("Hedron routes on plain FastAPI"), title="UI")


api.include_router(ui)
```

## What you still configure

| Concern | Responsibility |
|---|---|
| Session / CSRF middleware | Install yourself or copy patterns from `Hedron()` lifespan |
| Security policy on `app.state` | Set `hedron_security` |
| Static HTMX / assets | `mount_hedron_static` / build asset mounts |
| Explorer | Mount `hedron-explorer` only if you need it |

For most new apps, prefer `Hedron()` ([API](../api/HEDRON.md)). Use this path when
integrating into an existing FastAPI service. The [reference app](../examples/reference-app.md)
demonstrates both styles.

## See also

- [Router](../api/ROUTER.md) · [Responses](../api/RESPONSES.md) · [Authentication](authentication.md)
