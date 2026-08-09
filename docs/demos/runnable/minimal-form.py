import os

from fastapi import Form as FastAPIForm

from hedron import (
    CsrfField,
    Form,
    Hedron,
    Page,
    RefreshButton,
    Stack,
    SubmitButton,
    Text,
    TextInput,
    html,
    redirect_local,
    swap,
)

app = Hedron(
    title="Notes",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

notes_region = app.region("notes-count", description="Notes counter")
_NOTES: list[str] = []


def notes_panel():
    return html.div(
        Text(f"Notes saved: {len(_NOTES)}"),
        id=notes_region.id,
        role="status",
        aria={"live": "polite"},
    )


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            notes_panel(),
            RefreshButton.for_region(
                notes_region, href="/notes-count", label="Refresh notes count"
            ),
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


@app.fragment("/notes-count", region=notes_region)
def refresh_notes_count():
    return swap(notes_panel())


@app.action("/save", method="POST")
def save(note: str = FastAPIForm(...)):
    text = note.strip()
    if text:
        _NOTES.append(text)
    return redirect_local("/")
