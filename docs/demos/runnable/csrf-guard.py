import os

from fastapi import Request

from hedron import Hedron, Page, Stack, Text, csrf_token_for_request, html

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
            html.form(
                html.input(type="hidden", name="csrf_token", value=token),
                html.button("POST with CSRF", type="submit"),
                action="/do",
                method="post",
            ),
            html.form(
                html.button("POST without CSRF", type="submit"),
                action="/do",
                method="post",
            ),
        ),
        title="CSRF",
    )


@app.action("/do", method="POST")
def do_action() -> Page:
    return Page(Text("POST ok"), title="Done")
