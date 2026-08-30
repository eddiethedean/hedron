# Hardened sessions (application-owned)

!!! important "Not a core IdP"

    This recipe is **application-owned identity**. Hedron does not ship rotating
    refresh storage, token revocation, or an OIDC product. Use host sessions,
    your IdP, and optional helpers in `hedron.oidc` / `hedron.security`.

## Goals

- Short-lived access credentials plus **rotating refresh** tokens you store and revoke.
- Split CSRF strategy: **cookie session** forms use double-submit CSRF; **Bearer**
  API clients use `Authorization` and skip cookie CSRF (or use a separate anti-forgery
  scheme for cookie-authenticated SPA XHR).

## Rotating refresh (sketch)

1. On login / OIDC callback, create a server-side session (or refresh-token row) with
   `created` / `last_seen` stamps (`hedron.security.session_timeout.touch_session`).
2. Issue a short-lived access token (JWT or opaque) and a refresh token bound to that row.
3. On refresh: rotate the refresh token, invalidate the previous one, reject reuse.
4. On logout: delete the server row. **Signed cookies alone cannot revoke early** —
   clients may still present a valid cookie until max-age; server state is authoritative.

Stamp the session when login succeeds, then enforce both idle and absolute limits in the
same dependency used by protected pages and actions:

```python
import os
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from hedron import Hedron, Text
from hedron.security import SessionTimeoutError, check_session_timeout, touch_session

app = Hedron(
    title="Private workspace",
    security="standard",
    session_secret=os.environ["HEDRON_SESSION_SECRET"],
)


def establish_session(request: Request, user_id: str) -> None:
    request.session.clear()
    request.session["user_id"] = user_id
    touch_session(request.session)


def require_live_session(request: Request) -> str:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sign in required",
        )
    try:
        check_session_timeout(
            request.session,
            idle_seconds=30 * 60,
            absolute_seconds=8 * 60 * 60,
            touch=True,
        )
    except SessionTimeoutError as exc:
        request.session.clear()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired",
        ) from exc
    return str(user_id)


@app.page("/account")
def account(user_id: Annotated[str, Depends(require_live_session)]):
    return Text(f"Signed in as {user_id}")
```

Call `establish_session()` only after authentication succeeds. Immediate cross-device
revocation still requires a shared server-side session or refresh-token store.

## Cookie vs Bearer CSRF

| Client | Auth | CSRF |
|--------|------|------|
| Browser form / HTMX cookie session | Session cookie | Post-login `validate_csrf` + pre-auth `validate_login_csrf` on login POST |
| API / mobile Bearer | `Authorization` header | Cookie CSRF usually N/A; protect with CORS + token secrecy |

Do not treat browser `localStorage` as an authentication boundary.

## Related helpers

- Pre-auth login CSRF: `hedron.security.login_csrf`
- Idle/absolute timeout: `hedron.security.session_timeout`
- Auth route rate limits: `hedron.security.auth_rate_limit` (process-local; pair with ingress)
- Cache/Explorer parity: `mark_authenticated` / `install_authenticated_from_session`
- OIDC PKCE/state/claims: `hedron.oidc`
