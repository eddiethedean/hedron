import os

from fastapi import Form, Request, status
from fastapi.responses import RedirectResponse

from hedron import CsrfField, Form as HedronForm, Hedron, Page, Stack, SubmitButton, Text, TextInput

app = Hedron(
    title="Secure app",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

USERS = {"ada": "correct-horse"}


@app.page("/")
def login_page(request: Request) -> Page | RedirectResponse:
    if request.session.get("username"):
        return RedirectResponse("/home", status_code=status.HTTP_303_SEE_OTHER)
    return Page(
        Stack(
            Text("Sign in"),
            HedronForm(
                CsrfField(),
                TextInput("username", value="ada", required=True),
                TextInput("password", value="", type="password", required=True),
                SubmitButton("Sign in"),
                action="/login",
                method="post",
            ),
            Text("Demo only: ada / correct-horse"),
        ),
        title="Login",
    )


@app.action("/login", method="POST")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
) -> RedirectResponse:
    if USERS.get(username) != password:
        return RedirectResponse("/?error=1", status_code=status.HTTP_303_SEE_OTHER)
    request.session["username"] = username
    return RedirectResponse("/home", status_code=status.HTTP_303_SEE_OTHER)


@app.page("/home")
def home(request: Request) -> Page | RedirectResponse:
    username = request.session.get("username")
    if not username:
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    return Page(Text(f"Signed in as {username}"), title="Home")
