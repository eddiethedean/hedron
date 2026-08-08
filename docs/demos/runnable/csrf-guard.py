import os

from fastapi import Request

from hedron import (
    CsrfField,
    Form,
    Hedron,
    Hx,
    Page,
    Stack,
    SubmitButton,
    Text,
    csrf_token_for_request,
)

app = Hedron(
    title="CSRF demo",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)


def _csrf(request: Request) -> str:
    return csrf_token_for_request(request, request.app.state.hedron_security)


@app.page("/")
def home(request: Request) -> Page:
    token = _csrf(request)
    return Page(
        Stack(
            Text("GET seeds hedron_csrf"),
            Form(
                CsrfField(token=token),
                SubmitButton("POST with CSRF"),
                action="/do",
                method="post",
                hx=Hx(target="body", swap="outerHTML"),
            ),
            Form(
                SubmitButton("POST without CSRF"),
                action="/do",
                method="post",
            ),
        ),
        title="CSRF",
    )


@app.action("/do", method="POST")
def do_action() -> Page:
    return Page(Text("POST ok"), title="Done")
