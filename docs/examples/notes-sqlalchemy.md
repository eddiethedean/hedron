# Notes + SQLAlchemy

Minimal FastAPI + Hedron notes app with SQLite persistence and CSRF-safe POST.
Supports **create, list, and delete** — not a full admin CRUD surface.

## Run without cloning the monorepo

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: py -3 -m venv .venv && .\.venv\Scripts\Activate.ps1
pip install "hedron>=0.18.0,<0.19" "uvicorn[standard]" "sqlalchemy>=2.0"
# Copy https://raw.githubusercontent.com/eddiethedean/hedron/main/examples/notes-sqlalchemy/app.py → app.py
uvicorn app:app --reload
```

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
