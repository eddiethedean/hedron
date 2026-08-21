# Notes + SQLAlchemy

Minimal FastAPI + Hedron notes app with SQLite persistence (create / list / delete).

## Run without cloning

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: py -3 -m venv .venv && .\.venv\Scripts\Activate.ps1
pip install "hedron>=0.56.0,<0.58" "uvicorn[standard]" "sqlalchemy>=2.0"
curl -fsSL https://raw.githubusercontent.com/eddiethedean/hedron/main/examples/notes-sqlalchemy/app.py -o app.py
uvicorn app:app --reload
```

## Run (monorepo)

```bash
# From monorepo root (sqlalchemy is in the workspace dev group)
uv sync
uv run uvicorn app:app --app-dir examples/notes-sqlalchemy --reload
```

Open http://127.0.0.1:8000 — add or delete a note; data persists in `notes.db` beside
the process cwd (gitignored).

Guide: [docs/examples/notes-sqlalchemy.md](../../docs/examples/notes-sqlalchemy.md).
