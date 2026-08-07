# Notes + SQLAlchemy

Minimal FastAPI + Hedron notes app with SQLite persistence (create / list / delete).

## Run

```bash
# From monorepo root (sqlalchemy is in the workspace dev group)
uv sync
uv run uvicorn app:app --app-dir examples/notes-sqlalchemy --reload
```

Open http://127.0.0.1:8000 — add or delete a note; data persists in `notes.db` beside
the process cwd (gitignored).

Guide: [docs/examples/notes-sqlalchemy.md](../../docs/examples/notes-sqlalchemy.md).
