# OpenID Connect with Authlib

Hedron is not an identity provider. It supplies the application and signed host
session; Authlib performs the standard OIDC authorization-code exchange. Your app owns
provider registration, user records, roles, and authorization.

The runnable [`examples/oidc`](https://github.com/eddiethedean/hedron/tree/main/examples/oidc)
sample implements login, callback validation, a minimal identity session, error handling,
and CSRF-protected local logout.

## 1. Register the application

Create an OIDC web application with your provider and allow this development redirect:

```text
http://127.0.0.1:8000/auth/callback
```

Use the exact scheme, host, port, and path. `localhost` and `127.0.0.1` are different
redirect URIs to most providers.

## 2. Install and configure

```bash
pip install "hedron[auth]>=1.0.0" "uvicorn[standard]"
curl -fsSL https://raw.githubusercontent.com/eddiethedean/hedron/main/examples/oidc/app.py -o app.py
export OIDC_ISSUER="https://your-provider.example"
export OIDC_CLIENT_ID="your-client-id"
export OIDC_CLIENT_SECRET="your-client-secret"
export SESSION_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
uvicorn app:app --reload
```

The critical wiring in the runnable example is ordinary Authlib plus a small Hedron session
projection:

```python
import os
from collections.abc import Mapping

from fastapi import Request, status
from fastapi.responses import RedirectResponse

from hedron import Hedron
from hedron.auth import create_oauth_client, install_authenticated_from_session
from hedron.oidc import normalize_claims

app = Hedron(
    title="OIDC application",
    security="standard",
    explorer="off",
    session_secret=os.environ["SESSION_SECRET"],
)
install_authenticated_from_session(app, session_key="oidc_sub")

oauth = create_oauth_client()
provider = oauth.register(
    name="provider",
    client_id=os.environ["OIDC_CLIENT_ID"],
    client_secret=os.environ["OIDC_CLIENT_SECRET"],
    server_metadata_url=(
        f"{os.environ['OIDC_ISSUER'].rstrip('/')}/.well-known/openid-configuration"
    ),
    client_kwargs={"scope": "openid profile email"},
)


@app.get("/login")
async def login(request: Request) -> RedirectResponse:
    redirect_uri = os.environ.get(
        "OIDC_REDIRECT_URI",
        "http://127.0.0.1:8000/auth/callback",
    )
    return await provider.authorize_redirect(request, redirect_uri)


@app.get("/auth/callback")
async def callback(request: Request) -> RedirectResponse:
    token = await provider.authorize_access_token(request)
    raw_claims = token.get("userinfo")
    if not isinstance(raw_claims, Mapping):
        raw_claims = await provider.userinfo(token=token)
    claims = normalize_claims(raw_claims)

    request.session.clear()
    request.session["oidc_sub"] = claims.sub
    request.session["oidc_name"] = claims.name or claims.email or claims.sub
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
```

The complete example also catches provider errors and implements CSRF-protected local logout.
Keep those paths when adapting this excerpt; do not store access, refresh, or ID tokens in the
signed cookie session.

Open <http://127.0.0.1:8000>, choose **Sign in**, authenticate with the provider, and
confirm that the app displays the returned name. Sign out clears the local session.

## 3. Understand the security boundary

The example uses provider discovery, state validation, nonce/ID-token validation, and
the authorization-code exchange through Authlib. It stores only `sub` and a display
name in the signed session—not access, refresh, or ID tokens.

| Concern | Owner |
|---|---|
| Provider tenant and client registration | You / identity administrator |
| Protocol exchange and token validation | Authlib using provider metadata |
| Session cookie and rendered UI | Hedron / Starlette |
| User provisioning, roles, and object permissions | Your application |
| Provider logout, token revocation, and refresh | Your application policy |

For production, require HTTPS, rotate the session secret, use a shared server-side
session/token store when workers need shared state, set the provider's production
redirect URI exactly, and implement authorization independently of UI visibility.

## Common failures

| Symptom | Check |
|---|---|
| Provider reports `redirect_uri` mismatch | Registered URI exactly matches `OIDC_REDIRECT_URI` |
| Callback returns to the signed-out page | Cookie domain/HTTPS policy and a stable `SESSION_SECRET` |
| State validation fails | Login and callback used the same origin, browser session, and worker session store |
| Discovery fails | `OIDC_ISSUER` is the issuer base, not the authorization endpoint |
| Sign-in succeeds but access is too broad | Add application authorization; OIDC authentication alone grants no role |

Low-level URL, PKCE, state, nonce, and claim-redaction helpers remain available in
[`hedron.oidc`](../api/AUTH.md) for integrations that cannot use Authlib's Starlette
client. See also [authentication](authentication.md), [hardened sessions](hardened-sessions.md),
and the [threat model](threat-model.md).
