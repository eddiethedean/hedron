import os

from fastapi import Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from hedron import Hedron, Page, Stack, SubmitButton, Text, TextInput, html
from hedron.security import csrf_token_for_request

app = Hedron(
    title="Secure app",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

USERS = {"ada": "correct-horse"}


def _csrf(request: Request) -> str:
    return csrf_token_for_request(request, request.app.state.hedron_security)


def require_user(request: Request) -> str:
    username = request.session.get("username")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign in required")
    return str(username)


@app.page("/")
def login_page(request: Request) -> Page:
    token = _csrf(request)
    return Page(
        Stack(
            Text("Sign in"),
            html.form(
                html.input(type="hidden", name="csrf_token", value=token),
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    request.session["username"] = username
    return RedirectResponse("/home", status_code=303)


@app.page("/home")
def home(request: Request) -> Page:
    user = require_user(request)
    return Page(Text(f"Signed in as {user}"), title="Home")
