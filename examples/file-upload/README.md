# File upload

CSRF-safe multipart upload with size and type checks.

## Run without cloning

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: py -3 -m venv .venv && .\.venv\Scripts\Activate.ps1
pip install "hedron>=0.35.0,<0.36" "uvicorn[standard]"
curl -fsSL https://raw.githubusercontent.com/eddiethedean/hedron/main/examples/file-upload/app.py -o app.py
uvicorn app:app --reload
```

## Run (monorepo)

```bash
uv sync
uv run uvicorn app:app --app-dir examples/file-upload --reload
```

Open http://127.0.0.1:8000 — upload a small `.txt` or `.csv`.

Guide: [docs/examples/file-upload.md](../../docs/examples/file-upload.md).
