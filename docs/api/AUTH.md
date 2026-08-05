---
status: shipped
---

# Auth helpers


!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).

**Status:** Shipped in `0.6.0` · optional `hedron[auth]`

Hedron does **not** own identity, sessions, or claims. There is **no first-party
OIDC/SSO product**. The `hedron[auth]` extra exposes thin Authlib conveniences for
FastAPI/Starlette apps. Prefer the session-login pattern in
[Authentication](../guides/authentication.md) unless you need an OAuth provider.

```bash
pip install "hedron[auth]"
```

## `create_oauth_client(**kwargs)`

| Parameter | Type | Description |
|---|---|---|
| `**kwargs` | Authlib `OAuth` kwargs | Forwarded to Authlib’s Starlette `OAuth` registry |

**Returns:** an Authlib `OAuth` instance.

**Raises:** `HED-AUTH-0001` when Authlib is not installed.

## `OAuthHelper`

| Member | Signature | Description |
|---|---|---|
| `__init__` | `(oauth=None)` | Uses `create_oauth_client()` when `oauth` is omitted |
| `register` | `(name: str, **kwargs) -> Any` | Registers a provider; kwargs are Authlib `register` options |

```python
from fastapi import Request
from fastapi.responses import RedirectResponse

from hedron import Hedron, OAuthHelper, create_oauth_client, Page, Text

app = Hedron(title="OAuth demo", security="standard", session_secret="replace-in-production")
helper = OAuthHelper(create_oauth_client())
helper.register(
    "github",
    client_id="...",
    client_secret="...",
    access_token_url="https://github.com/login/oauth/access_token",
    authorize_url="https://github.com/login/oauth/authorize",
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "user:email"},
)


@app.get("/login/github")
async def login_github(request: Request):
    redirect_uri = request.url_for("auth_github")
    return await helper.oauth.github.authorize_redirect(request, redirect_uri)


@app.get("/auth/github")
async def auth_github(request: Request):
    token = await helper.oauth.github.authorize_access_token(request)
    # Persist identity yourself — Hedron does not invent a user model.
    request.session["username"] = token.get("userinfo", {}).get("login", "github-user")
    return RedirectResponse("/", status_code=303)


@app.page("/")
def home(request: Request) -> Page:
    return Page(Text(f"Hello {request.session.get('username', 'guest')}"), title="Home")
```

Applications remain responsible for login routes, session cookies, CSRF, and
authorization decisions (`Depends`, Django/Flask auth, or your IdP).

## Errors

| Code / condition | Behavior |
|---|---|
| Missing Authlib | Raises `HED-AUTH-0001` with install hint `pip install "hedron[auth]"` |
| Provider misconfiguration | Authlib/provider errors bubble to the route |

## See also

[Authentication guide](../guides/authentication.md) · [Security](../guides/security.md) ·
[Security types](SECURITY_TYPES.md)
