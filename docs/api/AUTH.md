---
status: shipped
---

# Auth helpers


!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).

**Status:** Shipped in `0.6.0` · optional `hedron[auth]`

Hedron does **not** own identity, sessions, or claims. The `hedron[auth]` extra exposes
thin Authlib conveniences for FastAPI/Starlette apps.

```bash
pip install "hedron[auth]"
```

## Helpers

| Symbol | Purpose |
|---|---|
| `create_oauth_client()` | Build an Authlib OAuth registry |
| `OAuthHelper` | Thin register/authorize helpers around Authlib |

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
authorization decisions.

## Errors

| Code / condition | Behavior |
|---|---|
| Missing Authlib | Raises `HED-AUTH-0001` with install hint `pip install "hedron[auth]"` |
| Provider misconfiguration | Authlib/provider errors bubble to the route |

## See also

[Security](../guides/security.md) · [Security types](SECURITY_TYPES.md)
