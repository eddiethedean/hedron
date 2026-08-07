# Session auth

Minimal session login gate with CSRF. Demo credentials only.

## Run

```bash
uv sync
uv run uvicorn app:app --app-dir examples/session-auth --reload
```

Open http://127.0.0.1:8000/login — sign in with `ada` / `correct-horse`.

Full guide narrative: [Authentication](https://hedron.readthedocs.io/en/latest/guides/authentication/).
