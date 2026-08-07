"""Notes list persisted with SQLAlchemy (SQLite). Local demo only."""

from __future__ import annotations

from fastapi import Form as FastAPIForm
from fastapi import Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import Column, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from hedron import Form, Hedron, Page, Stack, SubmitButton, Text, TextInput, html
from hedron.security import csrf_token_for_request

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


def _csrf(request: Request) -> str:
    return csrf_token_for_request(request, request.app.state.hedron_security)


@app.page("/")
def home(request: Request) -> Page:
    with Session(engine) as db:
        notes = list(db.scalars(select(Note).order_by(Note.id.desc())).all())
    token = _csrf(request)
    items = [html.li(Text(str(n.body))) for n in notes] or [html.li(Text("No notes yet."))]
    return Page(
        Stack(
            Text("Notes (SQLAlchemy + SQLite)"),
            Form(
                html.input(type="hidden", name="csrf_token", value=token),
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
    with SessionLocal() as db:
        db.add(Note(body=body.strip()[:500]))
        db.commit()
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
