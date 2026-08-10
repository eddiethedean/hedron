# Session auth

Minimal session login gate with CSRF. Demo credentials only.

## Run without cloning

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: py -3 -m venv .venv && .\.venv\Scripts\Activate.ps1
pip install "hedron>=0.26.0,<0.27" "uvicorn[standard]"
curl -fsSL https://raw.githubusercontent.com/eddiethedean/hedron/main/examples/session-auth/app.py -o app.py
uvicorn app:app --reload
```

## Run (monorepo)

```bash
uv sync
uv run uvicorn app:app --app-dir examples/session-auth --reload
```

Open http://127.0.0.1:8000 — you are redirected to `/login`. Sign in with
`ada` / `correct-horse` (not the reference-app Basic credentials).

Full guide narrative: [Authentication](https://hedron.readthedocs.io/en/latest/guides/authentication/).
