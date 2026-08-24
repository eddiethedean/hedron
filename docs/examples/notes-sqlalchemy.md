# Notes + SQLAlchemy

Minimal FastAPI + Hedron notes app with SQLite persistence and CSRF-safe POST.
Supports **create, list, and delete** — not a full admin CRUD surface.

### Try it (simulated)

=== "Demo"

    Same list pattern as the notes recipe — add and delete rows. Docs simulation (in-memory; the real recipe uses SQLAlchemy + SQLite).

    <!-- hedron-sim:crud-notes -->

=== "Code"

    Real recipe listing with SQLAlchemy + SQLite and HTMX fragment refresh. The Demo tab is a simplified in-memory HTMX list view:

    ```python title="app.py"
    """Notes list persisted with SQLAlchemy (SQLite). Local demo only.

    Create / list / delete — not a full admin CRUD app.
    """

    from __future__ import annotations

    from typing import Annotated

    from fastapi import HTTPException, status
    from pydantic import BaseModel, Field
    from sqlalchemy import Column, Integer, String, create_engine, select
    from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

    from hedron import (
        Control,
        CsrfField,
        Form,
        FormBody,
        Hedron,
        Page,
        Stack,
        SubmitButton,
        Text,
        html,
        refresh,
    )

    engine = create_engine("sqlite:///./notes.db", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


    class Base(DeclarativeBase):
        pass


    class Note(Base):
        __tablename__ = "notes"
        id = Column(Integer, primary_key=True)
        body = Column(String(500), nullable=False)


    class NoteIn(BaseModel):
        body: Annotated[str, Field(min_length=1, max_length=500), Control(label="Note")]


    class DeleteNote(BaseModel):
        note_id: int


    Base.metadata.create_all(bind=engine)

    app = Hedron(
        title="Notes",
        security="standard",
        explorer="off",
        session_secret="replace-in-production",
    )


    @app.refreshable("/notes")
    def notes():
        with Session(engine) as db:
            rows = list(db.scalars(select(Note).order_by(Note.id.desc())).all())
        items = [
            html.li(
                Text(str(row.body)),
                Form(
                    CsrfField(),
                    html.input(type="hidden", name="note_id", value=str(row.id)),
                    SubmitButton("Delete"),
                    action=delete,
                    style="display:inline",
                ),
            )
            for row in rows
        ]
        if not items:
            items = [html.li(Text("No notes yet."))]
        return html.ul(*items)


    @app.command("/save", fallback="/")
    def save(data: Annotated[NoteIn, FormBody()]):
        normalized = data.body.strip()
        if not normalized:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Note body must not be blank",
            )
        with SessionLocal() as db:
            db.add(Note(body=normalized[:500]))
            db.commit()
        return refresh(notes)


    @app.command("/delete", fallback="/")
    def delete(data: Annotated[DeleteNote, FormBody()]):
        with SessionLocal() as db:
            note = db.get(Note, data.note_id)
            if note is not None:
                db.delete(note)
                db.commit()
        return refresh(notes)


    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                Text("Notes (SQLAlchemy + SQLite) — create, list, delete"),
                save.form(),
                notes(),
            ),
            title="Notes",
        )
    ```

## Run without cloning the monorepo

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: py -3 -m venv .venv && .\.venv\Scripts\Activate.ps1
pip install "hedron>=0.60.2,<0.61" "uvicorn[standard]" "sqlalchemy>=2.0"
curl -fsSL https://raw.githubusercontent.com/eddiethedean/hedron/main/examples/notes-sqlalchemy/app.py -o app.py
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

- `@app.refreshable` notes list plus `@app.command` save/delete with `FormBody` / `refresh(notes)`
- SQLAlchemy ORM + SQLite (`notes.db` in the process working directory)
- HTMX fragment refresh with ordinary HTTP fallback to `/`

Source: [`examples/notes-sqlalchemy`](https://github.com/eddiethedean/hedron/tree/main/examples/notes-sqlalchemy).
Related: [Minimal form](../guides/minimal-form.md) · [Data apps](../guides/data-apps.md) ·
[Recipes](recipes/index.md) · [CRUD tutorial](crud-tutorial.md) (in-memory HTMX fragments).
