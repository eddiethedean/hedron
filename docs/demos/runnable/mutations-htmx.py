from __future__ import annotations

import os
from typing import Annotated

from fastapi import Form, Request

from hedron import Hedron, Page, Stack, SubmitButton, Text, TextInput, html
from hedron.security import csrf_token_for_request

app = Hedron(
    title="Mutations HTMX",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

result = app.region("save-result", description="Save result")


def _csrf(request: Request) -> str:
    return csrf_token_for_request(request, request.app.state.hedron_security)


@app.page("/")
def home(request: Request) -> Page:
    token = _csrf(request)
    return Page(
        Stack(
            html.form(
                html.input(type="hidden", name="csrf_token", value=token),
                TextInput(name="note", value="Ship the docs demo"),
                SubmitButton("Save"),
                method="post",
                **{
                    "hx-post": "/save",
                    "hx-target": result.selector,
                    "hx-swap": "innerHTML",
                },
            ),
            html.div(id=result.id, role="status", aria={"live": "polite"}),
        ),
        title="Mutations",
    )


@app.action("/save", method="POST", fragment_regions=(result,))
def save(note: Annotated[str, Form()] = "") -> object:
    return html.div(html.strong("Saved in region"), Text(note))
