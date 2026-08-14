# Authentication

Gate Hedron pages and actions with ordinary host-framework dependencies. Hedron does
not invent a second auth system—**you own login, password checks, and identity storage**.

!!! important "Not an IdP / managed SSO product"

    Hedron is still **not** an identity provider or managed SSO product. Optional FastAPI
    conveniences exist today—`hedron.oidc` (PKCE/state/nonce/URL builders, claim
    redaction) and `hedron.security` (login CSRF, session timeout stamps, auth rate
    limit, trusted-header identity) plus `mark_authenticated` /
    `install_authenticated_from_session`—but **apps must wire them**; host sessions
    remain authoritative. See [Hardened sessions](hardened-sessions.md).

## Complete minimal loop (session demo)

Canonical sample = [`examples/session-auth`](../examples/session-auth.md) (same Code
below). Demo credentials are for local learning only — replace with your IdP or
password store before production.

### Try it (simulated)

=== "Demo"

    Wrong password → soft redirect to /login?error=1. ada / correct-horse → signed-in panel. Docs simulation.

    <!-- hedron-sim:auth-login -->

=== "Code"

    Same `app.py` as the [session-auth recipe](../examples/session-auth.md): soft redirects, CSRF-safe sign-in, and logout. The Demo tab is a simplified view:

    ```python title="app.py"
    """Session login gate (demo credentials). Local learning only."""

    from __future__ import annotations

    from fastapi import Form as FastAPIForm
    from fastapi import Request, status
    from fastapi.responses import RedirectResponse

    from hedron import Alert, CsrfField, Form, Hedron, Page, Stack, SubmitButton, Text, TextInput

    app = Hedron(
        title="Session auth demo",
        security="standard",
        explorer="off",
        session_secret="replace-in-production",
    )

    # Demo only — never hard-code production passwords.
    USERS = {"ada": "correct-horse"}


    @app.page("/login")
    def login_page(request: Request, error: str | None = None) -> Page | RedirectResponse:
        if request.session.get("username"):
            return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
        feedback = (
            Alert("Invalid username or password.", tone="danger", title="Sign-in failed")
            if error == "1"
            else None
        )
        return Page(
            Stack(
                Text("Sign in (demo: ada / correct-horse)"),
                feedback,
                Form(
                    CsrfField(),
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
        username: str = FastAPIForm(...),
        password: str = FastAPIForm(...),
    ) -> RedirectResponse:
        if USERS.get(username) != password:
            return RedirectResponse("/login?error=1", status_code=status.HTTP_303_SEE_OTHER)
        request.session["username"] = username
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


    @app.page("/")
    def home(request: Request) -> Page | RedirectResponse:
        username = request.session.get("username")
        if not username:
            # Soft landing — redirect to login instead of a bare 401.
            return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
        return Page(
            Stack(
                Text(f"Signed in as {username}"),
                Form(
                    CsrfField(),
                    SubmitButton("Sign out"),
                    action="/logout",
                    method="post",
                ),
            ),
            title="Home",
        )


    @app.action("/logout", method="POST")
    def logout(request: Request) -> RedirectResponse:
        request.session.clear()
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    ```

```bash
curl -fsSL https://raw.githubusercontent.com/eddiethedean/hedron/main/examples/session-auth/app.py -o app.py
pip install "hedron>=0.39.0,<0.40" "uvicorn[standard]"
uvicorn app:app --reload
```

Open `/login`, sign in as `ada` / `correct-horse`, then visit `/`. Logout POSTs with
CSRF and clears the session.

### Protect a router prefix with `Depends`

For FastAPI dependency-style gates (beyond the soft redirect above):

```python
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from hedron import HedronRouter


def require_user(request: Request) -> str:
    username = request.session.get("username")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign in required")
    return str(username)


users = HedronRouter(prefix="/users", dependencies=[Depends(require_user)])
```

## Sessions

`Hedron(enable_sessions=True)` (default) installs Starlette `SessionMiddleware`
using `session_secret`. Store only non-sensitive session markers you need for
identity; keep credentials in your IdP or password store.

Prefer POST logout with CSRF (as above). Never put secrets in the signed cookie
beyond an opaque user id or username.

## Optional helpers (you wire)

These are conveniences, not a product. Authorization decisions (roles, object ACL)
remain application code—never inferred from component props.

!!! note "OIDC — complete provider-neutral example"

    Install `hedron[auth]` for the runnable login/callback/local-logout example.
    Hedron still does **not** provide an IdP, user database, or authorization policy.
    Follow the [OIDC guide](oidc.md), then apply your provider's registration and
    production-hardening requirements. The session demo above remains the simplest
    first-hour auth path.

```python
# OIDC handshake / URL builders / claim redaction (needs hedron[auth] for Authlib URLs)
from hedron.oidc import (
    generate_pkce,
    generate_state,
    generate_nonce,
    login_url,
    redact_claims,
    store_oidc_handshake,
)

# Login CSRF, idle/absolute stamps, auth rate limit, proxy headers
from hedron.security import (
    issue_login_csrf,
    validate_login_csrf,
    touch_session,
    check_session_timeout,
    auth_rate_limit_dependency,
    TrustedHeaderIdentity,
)

# Cache / Explorer parity with an existing host session key
from hedron.auth import mark_authenticated, install_authenticated_from_session
```

Full session hardening recipe: [Hardened sessions](hardened-sessions.md). API detail:
[Auth API](../api/AUTH.md).

### Host IdP patterns (you own)

| Host | Typical approach |
|---|---|
| FastAPI | Session cookie (this page) · OAuth/OIDC via Authlib or your API gateway · HTTP Basic only for demos |
| Django | `django.contrib.auth` · django-allauth / mozilla-django-oidc · middleware + `login_required` |
| Flask | Flask-Login · authlib Flask client · reverse-proxy SSO headers |

Hedron routes remain ordinary view callables — wrap them with the same dependencies /
decorators you use for JSON APIs.

### Flask-Login → `AuthSignal` (optional)

`hedron-flask` does **not** require Flask-Login. When `flask_login` is importable,
`HedronFlask.auth_signal()` prefers an authenticated `current_user` (`get_id()` /
`id`) so private-cache headers and Explorer/job signals follow the same identity.
Otherwise it falls back to `session["user_id"]` or `session["_user_id"]` (plus optional
`scopes` / `tenant_id` session keys).

```python
from flask import Flask
from flask_login import LoginManager, UserMixin, login_user

from hedron_flask import HedronFlask

app = Flask(__name__)
app.secret_key = "replace-in-production"
hedron = HedronFlask()
hedron.init_app(app)

login_manager = LoginManager(app)


class User(UserMixin):
    def __init__(self, user_id: str) -> None:
        self.id = user_id


@login_manager.user_loader
def load_user(user_id: str) -> User:
    return User(user_id)


@app.get("/login-demo")
def login_demo():
    login_user(User("ada"))
    signal = hedron.auth_signal()
    # signal.authenticated is True; subject_id == "ada"
    return {"subject_id": signal.subject_id}
```

Apps that only set `session["user_id"]` without Flask-Login keep working. Redaction and
`Cache-Control: private, no-store` for authenticated responses are unchanged.

## Explorer

`explorer="development"` is for local use. For rare shared environments, use
`explorer="secured"` with `explorer_dependencies=` that enforce real auth. Keep
Explorer off in production.

## See also

- [OIDC helpers](oidc.md) · [Hardened sessions](hardened-sessions.md) · [Security](security.md)
- [Threat model](threat-model.md) · [Minimal form POST](minimal-form.md)
- [Auth API](../api/AUTH.md) · [State](../api/STATE.md)
- [Session auth recipe](../examples/session-auth.md) ·
  [Reference app](../examples/reference-app.md) (HTTP Basic demo credentials)
