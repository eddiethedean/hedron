---
status: shipped
---

# Auth and OIDC helpers


!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).
    Package maturity (Beta) is separate from API level (`beta`).

**Status:** Shipped · optional `hedron[auth]` · **API level `beta`**

Hedron does **not** own identity, sessions, or claims. There is **no first-party
IdP / managed SSO product**. Host frameworks and your application own login cookies,
authorization, and multi-tenant isolation.

Two helper layers exist under `hedron[auth]` (Authlib):

1. **OIDC conveniences** (`hedron.oidc`) — PKCE/state/nonce, claim normalization,
   Explorer-safe redaction, Authlib-backed authorize/logout URL builders.
2. **Generic OAuth registry** (`OAuthHelper` / `create_oauth_client`) — thin Authlib
   Starlette `OAuth` wrappers for non-OIDC or custom providers.

Prefer the session-login pattern in [Authentication](../guides/authentication.md)
unless you need an external provider.

```bash
pip install "hedron[auth]>=0.61.0,<0.62"
```

## OIDC helpers (`hedron.oidc`)

Import from `hedron.oidc` (not re-exported on `hedron.__all__`). These helpers never
create a user table or infer authorization — they only assist handshake hygiene.

| Symbol | Role |
|---|---|
| `OidcClientConfig` | Issuer, client id/secret, redirect URI, scopes, optional authorize/logout URLs |
| `generate_state` / `generate_nonce` / `generate_pkce` | CSRF/replay-resistant handshake material |
| `store_oidc_handshake` | Persist handshake secrets in the **host** session under a Hedron key |
| `validate_callback_state` / `validate_callback_nonce` | Compare callback parameters to the stored handshake |
| `normalize_claims` / `OidcUserClaims` | Map IdP claims to a small `sub` / `email` / `name` view |
| `redact_claims` | Strip secret-like keys for Explorer / logs |
| `login_url` / `logout_url` | Authlib-backed authorize / end-session URL builders |

```python
from hedron.oidc import (
    OidcClientConfig,
    generate_pkce,
    generate_state,
    login_url,
    store_oidc_handshake,
)

config = OidcClientConfig(
    issuer="https://idp.example/",
    client_id="app",
    redirect_uri="https://app.example/auth/callback",
    client_secret="…",  # or None for public + PKCE
)
pkce = generate_pkce()
state = generate_state()
store_oidc_handshake(request.session, state=state, code_verifier=pkce.verifier)
# Redirect the browser to login_url(config, state=state, code_challenge=pkce.challenge)
```

Full walkthrough: [Authentication](../guides/authentication.md).

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

## `SessionAuthFlow` (0.60)

Compose login/logout/session page plumbing around **explicit** application identity
callbacks. Not an IdP, user database, password hasher, or authorization framework.

```python
from hedron import (
    AuthDenied,
    AuthSuccess,
    Hedron,
    RateLimitPolicy,
    SessionAuthFlow,
)

# credentials: Pydantic model; authenticate returns AuthSuccess | AuthDenied
auth = SessionAuthFlow(
    credentials=Credentials,
    authenticate=authenticate_user,
    serialize_principal=lambda principal: principal,
    load_principal=lambda stored: stored,
    login_path="/login",
    logout_path="/logout",
    after_login="/",
    rate_limit=RateLimitPolicy(limit=20, window_seconds=60.0),
    rotation="on_login",
)
app.include_feature(auth)
# Use Depends(auth.current_principal()) on protected screens/commands
```

Recipe: [Session auth](../examples/session-auth.md).

## Errors

| Code / condition | Behavior |
|---|---|
| Missing Authlib | Raises `HED-AUTH-0001` with install hint `pip install "hedron[auth]>=0.61.0,<0.62"` |
| Invalid `OidcClientConfig` | `ValueError` on empty issuer / client_id / redirect_uri |
| Provider misconfiguration | Authlib/provider errors bubble to the route |
| Unsafe `after_login` / missing rate limit | `SessionAuthFlow` fails closed (`HED-AUTHFLOW-*`) |

## See also

[Authentication guide](../guides/authentication.md) · [Security](../guides/security.md) ·
[Security types / SecurityPolicy](SECURITY_TYPES.md) · Autodoc OIDC section
