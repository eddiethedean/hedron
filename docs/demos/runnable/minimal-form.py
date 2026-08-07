import os

from fastapi import Form, Request

from hedron import Hedron, Page, Stack, SubmitButton, Text, TextInput, csrf_token_for_request, html

app = Hedron(
    title="Notes",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)


def _csrf(request: Request) -> str:
    return csrf_token_for_request(request, request.app.state.hedron_security)


@app.page("/")
def notes(request: Request) -> Page:
    token = _csrf(request)
    return Page(
        Stack(
            Text("Leave a note"),
            html.form(
                html.input(type="hidden", name="csrf_token", value=token),
                TextInput("note", value="Ship the docs demo", required=True),
                SubmitButton("Save"),
                action="/save",
                method="post",
            ),
        ),
        title="Notes",
    )


@app.action("/save", method="POST")
def save(note: str = Form(...)) -> Page:
    return Page(Text(f"Saved: {note}"), title="Saved")
