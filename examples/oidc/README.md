# OIDC authorization-code example

This is a complete, provider-neutral OIDC login/callback/local-logout loop using
Hedron's host session and Authlib. It does not create users or decide permissions.

Register `http://127.0.0.1:8000/auth/callback` as an allowed redirect URI with your
provider, then run:

```bash
python -m venv .venv && source .venv/bin/activate
pip install "hedron[auth]>=1.0.1,<1.1" "uvicorn[standard]"
export OIDC_ISSUER="https://your-provider.example"
export OIDC_CLIENT_ID="your-client-id"
export OIDC_CLIENT_SECRET="your-client-secret"
export SESSION_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
curl -fsSL https://raw.githubusercontent.com/eddiethedean/hedron/main/examples/oidc/app.py -o app.py
uvicorn app:app --reload
```

Open <http://127.0.0.1:8000>. For a non-default origin, also set
`OIDC_REDIRECT_URI` to the exact registered callback URL.

Before production, use HTTPS, a shared server-side session store when appropriate,
provider logout/revocation if required, and application-specific authorization. See the
[OIDC guide](https://hedron.readthedocs.io/en/latest/guides/oidc/).

