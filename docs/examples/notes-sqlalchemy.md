# Notes + SQLAlchemy

Minimal FastAPI + Hedron notes app with SQLite persistence and CSRF-safe POST.
Supports **create, list, and delete** — not a full admin CRUD surface.

## Run (monorepo)

```bash
uv sync
uv run uvicorn app:app --app-dir examples/notes-sqlalchemy --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Notes persist in `notes.db` in the
process working directory (gitignored).

## What it shows

- `@app.page` + `@app.action` with a small `_csrf(request)` helper
- SQLAlchemy ORM + SQLite
- Post-Redirect-Get after save / delete

Source: [`examples/notes-sqlalchemy`](https://github.com/eddiethedean/hedron/tree/main/examples/notes-sqlalchemy).
Related: [Minimal form](../guides/minimal-form.md) · [Data apps](../guides/data-apps.md) ·
[Recipes](recipes/index.md).
