# Authentication

Gate Hedron pages and actions with ordinary host-framework dependencies. Hedron does
not invent a second auth system—**you own login, password checks, and identity storage**.

!!! important "No first-party IdP / OIDC product"

    Hedron does **not** ship OIDC, SAML, SSO, or a managed identity provider. Optional
    `hedron[auth]` Authlib helpers are convenience wrappers only. Plan IdP integration
    with FastAPI/Django/Flask patterns (or your org’s gateway) before enterprise rollout.
    OIDC-oriented helpers may appear on the roadmap later; they are not a substitute for
    host identity today.

## Complete minimal loop (session demo)

Demo credentials below are for local learning only. Replace with your IdP or
password store before production.

```python title="app.py"
from typing import Annotated

from fastapi import Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from hedron import Hedron, Page, Stack, SubmitButton, Text, TextInput, html
from hedron.security import csrf_token_for_request

app = Hedron(
    title="Secure app",
    security="standard",
    session_secret="replace-in-production",
)

# Demo only — never hard-code production passwords.
USERS = {"ada": "correct-horse"}


def require_user(request: Request) -> str:
    username = request.session.get("username")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sign in required",
        )
    return str(username)


def _csrf(request: Request) -> str:
    return csrf_token_for_request(request, request.app.state.hedron_security)


@app.page("/login")
def login_page(request: Request) -> Page:
    if request.session.get("username"):
        return Page(Text("Already signed in"), title="Login")
    token = _csrf(request)
    return Page(
        Stack(
            Text("Sign in"),
            html.form(
                html.input(type="hidden", name="csrf_token", value=token),
                TextInput("username", value="", required=True),
                TextInput("password", value="", type="password", required=True),
                SubmitButton("Sign in"),
                action="/login",
                method="post",
            ),
        ),
        title="Login",
    )


@app.action("/login", method="POST")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
) -> RedirectResponse:
    if USERS.get(username) != password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    request.session["username"] = username
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@app.action("/logout", method="POST")
def logout(request: Request) -> RedirectResponse:
    request.session.clear()
    return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)


@app.page("/")
def home(
    request: Request,
    username: Annotated[str, Depends(require_user)],
) -> Page:
    token = _csrf(request)
    return Page(
        Stack(
            Text(f"Signed in as {username}"),
            html.form(
                html.input(type="hidden", name="csrf_token", value=token),
                SubmitButton("Sign out"),
                action="/logout",
                method="post",
            ),
        ),
        title="Home",
    )
```

Run `uv run uvicorn app:app --reload`, open `/login`, sign in as `ada` /
`correct-horse`, then visit `/`. Logout POSTs with CSRF and clears the session.

Apply the same `Depends(require_user)` to `@app.component` / `@app.action` routes,
or attach dependencies on a `HedronRouter` so a whole prefix is protected:

```python
from hedron import HedronRouter

users = HedronRouter(prefix="/users", dependencies=[Depends(require_user)])
```

## Sessions

`Hedron(enable_sessions=True)` (default) installs Starlette `SessionMiddleware`
using `session_secret`. Store only non-sensitive session markers you need for
identity; keep credentials in your IdP or password store.

Prefer POST logout with CSRF (as above). Never put secrets in the signed cookie
beyond an opaque user id or username.

## Optional Authlib helpers

Install `hedron[auth]` when you want Authlib-oriented helpers. Authorization
decisions (roles, object ACL) remain application code—never inferred from
component props. See [Auth API](../api/AUTH.md).

### Host IdP patterns (you own)

| Host | Typical approach |
|---|---|
| FastAPI | Session cookie (this page) · OAuth/OIDC via Authlib or your API gateway · HTTP Basic only for demos |
| Django | `django.contrib.auth` · django-allauth / mozilla-django-oidc · middleware + `login_required` |
| Flask | Flask-Login · authlib Flask client · reverse-proxy SSO headers |

Hedron routes remain ordinary view callables — wrap them with the same dependencies /
decorators you use for JSON APIs.

## Explorer

`explorer="development"` is for local use. For rare shared environments, use
`explorer="secured"` with `explorer_dependencies=` that enforce real auth. Keep
Explorer off in production.

## See also

- [Security](security.md) · [Threat model](threat-model.md)
- [Minimal form POST](minimal-form.md) · [Auth API](../api/AUTH.md) · [State](../api/STATE.md)
- [Reference app walkthrough](../examples/reference-app.md) (HTTP Basic demo credentials)
