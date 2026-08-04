---
status: shipped
---

# Auth helpers


!!! note "Stability (0.8 compatibility baseline)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Shipped in `0.6.0`

Hedron does **not** own identity, sessions, or claims. The `hedron[auth]` extra exposes
thin Authlib conveniences for FastAPI/Starlette apps.

```bash
pip install "hedron[auth]"
```

```python
from hedron import OAuthHelper, create_oauth_client

oauth = create_oauth_client()
helper = OAuthHelper(oauth)
helper.register(
    "github",
    client_id="...",
    client_secret="...",
    access_token_url="https://github.com/login/oauth/access_token",
    authorize_url="https://github.com/login/oauth/authorize",
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "user:email"},
)
```

Applications remain responsible for login routes, session cookies, CSRF, and
authorization decisions. Missing Authlib raises `HED-AUTH-0001` with
`pip install "hedron[auth]"`.

For Hedron's own CSRF / security profiles, see [Security](../guides/security.md).
