# Session auth

Minimal session login gate with CSRF. Demo credentials only — replace before any deploy.

## Run without cloning the monorepo

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: py -3 -m venv .venv && .\.venv\Scripts\Activate.ps1
pip install "hedron>=0.18.0,<0.19" "uvicorn[standard]"
# Copy https://raw.githubusercontent.com/eddiethedean/hedron/main/examples/session-auth/app.py → app.py
uvicorn app:app --reload
```

## Run (monorepo)

```bash
uv sync
uv run uvicorn app:app --app-dir examples/session-auth --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) — unauthenticated visits **redirect to
`/login`**. Sign in with `ada` / `correct-horse`.

## What it shows

- Starlette session cookie via `Hedron(session_secret=...)`
- Soft landing redirect (not a bare 401) when `/` is unauthenticated
- CSRF-safe login and logout POSTs

Source: [`examples/session-auth`](https://github.com/eddiethedean/hedron/tree/main/examples/session-auth).
Full narrative: [Authentication](../guides/authentication.md).
