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


@app.view("/notes")
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


@app.action("/save", fallback="/")
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


@app.action("/delete", fallback="/")
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
