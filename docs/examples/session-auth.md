# Session auth

Minimal session login gate with CSRF. Demo credentials only — replace before any deploy.

## Run (monorepo)

```bash
uv sync
uv run uvicorn app:app --app-dir examples/session-auth --reload
```

Open [http://127.0.0.1:8000/login](http://127.0.0.1:8000/login). Sign in with
`ada` / `correct-horse`, then visit `/`.

## What it shows

- Starlette session cookie via `Hedron(session_secret=...)`
- `Depends(require_user)` on pages
- CSRF-safe login and logout POSTs

Source: [`examples/session-auth`](https://github.com/eddiethedean/hedron/tree/main/examples/session-auth).
Full narrative: [Authentication](../guides/authentication.md).
