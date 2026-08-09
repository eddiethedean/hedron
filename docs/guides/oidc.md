# OIDC helpers (not an IdP product)

!!! important "Helpers only"

    Hedron does **not** ship a managed SSO product or a complete pasteable OIDC app.
    `hedron[auth]` provides Authlib-backed URL/PKCE/state helpers. **You** own the IdP
    configuration, token exchange, user store, and authorization. Prefer the
    [session-auth recipe](../examples/session-auth.md) for first-hour auth.

Pin: `pip install "hedron[auth]>=0.25.0,<0.26"`.

## Wiring outline

1. **Install** `hedron[auth]` and configure your IdP (issuer, client id/secret, redirect URI).
2. **Login route** — generate PKCE/state/nonce, `store_oidc_handshake` in the host session,
   redirect to `login_url(...)`.
3. **Callback route** — `validate_callback_state` / nonce, exchange the code with Authlib
   (your code), `normalize_claims`, then mark the host session
   (`mark_authenticated` / set your own session keys).
4. **Logout** — clear session; optional `logout_url(...)` to the IdP end-session endpoint.
5. **Gate pages** — ordinary FastAPI `Depends` / soft redirects, same as
   [Authentication](authentication.md).

```python
from hedron.oidc import (
    OidcClientConfig,
    generate_pkce,
    generate_state,
    generate_nonce,
    login_url,
    store_oidc_handshake,
    validate_callback_state,
)

config = OidcClientConfig(
    issuer="https://idp.example/",
    client_id="app",
    redirect_uri="https://app.example/auth/callback",
)
# Build authorize URL + store handshake secrets in request.session — see Auth API.
```

Symbol reference: [Auth API](../api/AUTH.md). Session hardening:
[Hardened sessions](hardened-sessions.md).

## What you still bring

| Concern | Owner |
|---|---|
| IdP tenant / app registration | You / IdP admin |
| Authorization code → tokens exchange | Your Authlib (or gateway) code |
| Roles / object ACL | Your app |
| Multi-worker session store | Sticky sessions or shared store |

## See also

- [Authentication](authentication.md) · [Auth API](../api/AUTH.md) · [What’s ready](whats-ready.md)
