"""Notes list persisted with SQLAlchemy (SQLite). Local demo only.

Create / list / delete — not a full admin CRUD app.
"""

from __future__ import annotations

from fastapi import Form as FastAPIForm
from fastapi import HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import Column, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from hedron import CsrfField, Form, Hedron, Page, Stack, SubmitButton, Text, TextInput, html

engine = create_engine("sqlite:///./notes.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True)
    body = Column(String(500), nullable=False)


Base.metadata.create_all(bind=engine)

app = Hedron(
    title="Notes",
    security="standard",
    explorer="off",
    session_secret="replace-in-production",
)


@app.page("/")
def home(request: Request) -> Page:
    with Session(engine) as db:
        notes = list(db.scalars(select(Note).order_by(Note.id.desc())).all())
    items = []
    for n in notes:
        items.append(
            html.li(
                Text(str(n.body)),
                Form(
                    CsrfField(),
                    html.input(type="hidden", name="note_id", value=str(n.id)),
                    SubmitButton("Delete"),
                    action="/delete",
                    method="post",
                    style="display:inline",
                ),
            )
        )
    if not items:
        items = [html.li(Text("No notes yet."))]
    return Page(
        Stack(
            Text("Notes (SQLAlchemy + SQLite) — create, list, delete"),
            Form(
                CsrfField(),
                TextInput("body", value="", required=True, placeholder="Write a note"),
                SubmitButton("Save"),
                action="/save",
                method="post",
            ),
            html.ul(*items),
        ),
        title="Notes",
    )


@app.action("/save", method="POST")
def save(body: str = FastAPIForm(...)) -> RedirectResponse:
    normalized = body.strip()
    if not normalized:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Note body must not be blank",
        )
    with SessionLocal() as db:
        db.add(Note(body=normalized[:500]))
        db.commit()
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@app.action("/delete", method="POST")
def delete(note_id: int = FastAPIForm(...)) -> RedirectResponse:
    with SessionLocal() as db:
        note = db.get(Note, note_id)
        if note is not None:
            db.delete(note)
            db.commit()
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
