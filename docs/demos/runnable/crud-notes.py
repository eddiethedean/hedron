from __future__ import annotations

import os
from typing import Annotated
from uuid import uuid4

from fastapi import Form, Request

from hedron import CsrfField, Hedron, Page, Stack, SubmitButton, Text, TextInput, html

app = Hedron(
    title="CRUD notes",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "replace-in-production"),
)

NOTES: dict[str, str] = {}
listing = app.region("notes-list", description="Notes list")


def render_list(request: Request):
    del request  # request kept for signature parity with fragment handlers
    if not NOTES:
        return html.div(Text("No notes yet."), id=listing.id)
    items = []
    for note_id, body in NOTES.items():
        items.append(
            html.li(
                Text(body),
                " ",
                html.form(
                    CsrfField(),
                    html.input(type="hidden", name="note_id", value=note_id),
                    SubmitButton("Delete"),
                    method="post",
                    **{
                        "hx-post": "/notes/delete",
                        "hx-target": listing.selector,
                        "hx-swap": "outerHTML",
                    },
                ),
            )
        )
    return html.div(html.ul(*items), id=listing.id)


@app.page("/")
def home(request: Request) -> Page:
    return Page(
        Stack(
            render_list(request),
            html.form(
                CsrfField(),
                TextInput(name="note", placeholder="New note"),
                SubmitButton("Add note"),
                method="post",
                **{
                    "hx-post": "/notes",
                    "hx-target": listing.selector,
                    "hx-swap": "outerHTML",
                },
            ),
        ),
        title="CRUD",
    )


@app.action("/notes", method="POST", fragment_regions=(listing,))
def add_note(request: Request, note: Annotated[str, Form()] = "") -> object:
    text = note.strip()
    if text:
        NOTES[str(uuid4())] = text
    return render_list(request)


@app.action("/notes/delete", method="POST", fragment_regions=(listing,))
def delete_note(request: Request, note_id: Annotated[str, Form()] = "") -> object:
    NOTES.pop(note_id, None)
    return render_list(request)
