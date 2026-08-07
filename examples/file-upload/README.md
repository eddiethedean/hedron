# File upload

CSRF-safe multipart upload with size and type checks.

## Run

```bash
uv sync
uv run uvicorn app:app --app-dir examples/file-upload --reload
```

Open http://127.0.0.1:8000 — upload a small `.txt` or `.csv`.
