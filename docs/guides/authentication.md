# Authentication

Gate Hedron pages and actions with ordinary FastAPI dependencies. Hedron does not
invent a second auth system.

## Pattern

```python
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from hedron import Hedron, Page, Text
from hedron.security import SecurityPolicy, csrf_token_for_request

app = Hedron(
    title="Secure app",
    security="standard",
    session_secret="replace-in-production",
)


def require_user(request: Request) -> str:
    username = request.session.get("username")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign in required")
    return str(username)


@app.page("/")
def home(
    request: Request,
    username: Annotated[str, Depends(require_user)],
) -> Page:
    policy = getattr(request.app.state, "hedron_security", SecurityPolicy.from_name("standard"))
    token = csrf_token_for_request(request, policy)
    return Page(Text(f"Signed in as {username} (csrf ready)"), title="Home")
```

Apply the same `Depends(require_user)` to `@app.component` / `@app.action` routes,
or attach dependencies on a `HedronRouter` so a whole prefix is protected.

## Sessions

`Hedron(enable_sessions=True)` (default) installs Starlette `SessionMiddleware`
using `session_secret`. Store only non-sensitive session markers you need for
identity; keep credentials in your IdP or password store.

Login/logout are application routes: set `request.session["username"] = ...` on
successful authentication and `request.session.clear()` on logout. Prefer POST
logout with CSRF.

## Optional Authlib helpers

Install `hedron[auth]` when you want Authlib-oriented helpers. Authorization
decisions (roles, object ACL) remain application code—never inferred from
component props.

## Explorer

`explorer="development"` is for local use. For rare shared environments, use
`explorer="secured"` with `explorer_dependencies=` that enforce real auth. Keep
Explorer off in production.

## See also

- [Security](security.md) · [Threat model](threat-model.md)
- [Auth API](../api/AUTH.md) · [State](../api/STATE.md)
- [Reference app walkthrough](../examples/reference-app.md)
