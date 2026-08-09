# Existing / plain FastAPI + HedronRouter

Use Hedron’s routing and HTML responses without the `Hedron()` facade when you
already own a `FastAPI` app. You must install session and security middleware yourself.

Prefer [`hedron new`](../getting-started/quickstart.md) for the first-hour Refresh demo.
This page is the **existing-app** path.

!!! warning "FastAPI pin — Supported vs declared"

    For a known-good first mount, use FastAPI `>=0.141.1,<0.142` (CI-supported). Declared
    metadata allows up to `<0.150`, but versions outside Supported are not CI-proven.
    Shared or older FastAPI environments often fail to resolve — use a **clean venv**.
    See [troubleshooting](troubleshooting.md) and [Compatibility](../COMPATIBILITY.md).

Minimal include:

```python
from fastapi import FastAPI
from hedron import HedronRouter, Page, Text, mount_hedron_static

api = FastAPI()
mount_hedron_static(api)
ui = HedronRouter(prefix="/ui")


@ui.page("/")
def home() -> Page:
    return Page(Text("Hello from Hedron"), title="Home")


api.include_router(ui)
```

Full listing with CSRF and sessions:

```python title="app.py"
from fastapi import FastAPI, Form, Request
from starlette.middleware.sessions import SessionMiddleware

from hedron import HedronRouter, Page, SubmitButton, Text, TextInput, html, mount_hedron_static
from hedron.security import (
    SecurityHeadersMiddleware,
    SecurityPolicy,
    csrf_token_for_request,
)
from hedron.security.csrf import ensure_csrf_cookie

api = FastAPI(title="Existing API")
policy = SecurityPolicy.from_name("standard")
api.state.hedron_security = policy

api.add_middleware(SessionMiddleware, secret_key="replace-in-production")
api.add_middleware(SecurityHeadersMiddleware, policy=policy)
mount_hedron_static(api)

ui = HedronRouter(prefix="/ui")


@ui.page("/")
def home(request: Request) -> Page:
    token = csrf_token_for_request(request, policy)
    page = Page(
        html.form(
            html.input(type="hidden", name="csrf_token", value=token),
            TextInput("note", value=""),
            SubmitButton("Save"),
            action="/ui/save",
            method="post",
        ),
        title="UI",
    )
    return page


@ui.action("/save", method="POST")
def save(note: str = Form(...)) -> Page:
    return Page(Text(f"Saved: {note}"), title="Saved")


api.include_router(ui)


@api.middleware("http")
async def seed_csrf_cookie(request: Request, call_next):
    response = await call_next(request)
    if request.method.upper() in {"GET", "HEAD", "OPTIONS"}:
        token = csrf_token_for_request(request, policy)
        ensure_csrf_cookie(response, policy, token=token, request=request)
    return response
```

`HedronRouter` still validates CSRF on unsafe page/component/action methods when
`app.state.hedron_security` is set. The middleware above seeds the cookie on safe GETs
the way `Hedron()` does.

## Errors you must handle yourself

| Situation | Behavior on this path |
|---|---|
| CSRF missing/invalid on unsafe method | HTTP 403 from Hedron route CSRF when policy is set |
| FastAPI outside `>=0.141.1,<0.142` | Install / resolver failure — clean venv or pin FastAPI |
| Missing session middleware | Session/CSRF features break — install `SessionMiddleware` |
| Production without build manifest | Prefer `Hedron(production=True)` path or run `hedron build` yourself |

## What you still configure

| Concern | Responsibility |
|---|---|
| Session middleware | `SessionMiddleware` with a real secret |
| Security headers | `SecurityHeadersMiddleware` |
| Security policy on `app.state` | Set `hedron_security` |
| CSRF cookie seeding | Safe-GET middleware or equivalent (see above) |
| Static HTMX / assets | `mount_hedron_static` / build asset mounts |
| Explorer | Mount `hedron-explorer` only if you need it |
| Production build | `hedron build` + deploy `manifest.json` when using production gates |

For most new apps, prefer `Hedron()` ([API](../api/HEDRON.md)). Use **this
`HedronRouter` + `include_router` path** when integrating into an existing FastAPI
service. Mounting a full `Hedron()` sub-app with `api.mount(...)` is an alternate —
see [Mount](../api/MOUNT.md). The [reference app](../examples/reference-app.md)
demonstrates both styles.

## See also

- [Router](../api/ROUTER.md) · [Responses](../api/RESPONSES.md) · [Authentication](authentication.md)
- [Minimal form POST](minimal-form.md) · [Security](security.md)
