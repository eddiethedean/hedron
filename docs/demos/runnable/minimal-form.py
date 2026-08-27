import os
from datetime import UTC, datetime

from fastapi import Form as FastAPIForm

from hedron import (
    CsrfField,
    Form,
    Hedron,
    Page,
    Stack,
    SubmitButton,
    Text,
    TextInput,
    html,
    redirect_local,
)

app = Hedron(
    title="Notes",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

_NOTES: list[str] = []


@app.view("/status")
def status():
    stamp = datetime.now(UTC).strftime("%H:%M:%S UTC")
    return html.div(
        Text(f"All systems operational · refreshed {stamp}"),
        role="status",
        aria={"live": "polite"},
    )


@app.view("/notes-count")
def notes():
    return html.div(
        Text(f"Notes saved: {len(_NOTES)}"),
        role="status",
        aria={"live": "polite"},
    )


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            status(),
            status.refresh_button("Refresh status"),
            notes(),
            notes.refresh_button("Refresh notes count"),
            Text("Leave a note"),
            Form(
                CsrfField(),
                TextInput("note", value="Ship the docs demo", required=True),
                SubmitButton("Save"),
                action="/save",
                method="post",
            ),
        ),
        title="Notes",
    )


@app.action("/save", method="POST")
def save(note: str = FastAPIForm(...)):
    text = note.strip()
    if text:
        _NOTES.append(text)
    return redirect_local("/")
