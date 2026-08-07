"""Session login gate (demo credentials). Local learning only."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi import Form as FastAPIForm
from fastapi.responses import RedirectResponse

from hedron import Form, Hedron, Page, Stack, SubmitButton, Text, TextInput, html
from hedron.security import csrf_token_for_request

app = Hedron(
    title="Session auth demo",
    security="standard",
    explorer="off",
    session_secret="replace-in-production",
)

# Demo only — never hard-code production passwords.
USERS = {"ada": "correct-horse"}


def require_user(request: Request) -> str:
    username = request.session.get("username")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sign in required",
        )
    return str(username)


def _csrf(request: Request) -> str:
    return csrf_token_for_request(request, request.app.state.hedron_security)


@app.page("/login")
def login_page(request: Request) -> Page:
    if request.session.get("username"):
        return Page(Text("Already signed in"), title="Login")
    token = _csrf(request)
    return Page(
        Stack(
            Text("Sign in (demo: ada / correct-horse)"),
            Form(
                html.input(type="hidden", name="csrf_token", value=token),
                TextInput("username", value="", required=True),
                TextInput("password", value="", type="password", required=True),
                SubmitButton("Sign in"),
                action="/login",
                method="post",
            ),
        ),
        title="Login",
    )


@app.action("/login", method="POST")
def login(
    request: Request,
    username: str = FastAPIForm(...),
    password: str = FastAPIForm(...),
) -> RedirectResponse:
    if USERS.get(username) != password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad credentials")
    request.session["username"] = username
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@app.page("/")
def home(
    request: Request,
    username: Annotated[str, Depends(require_user)],
) -> Page:
    token = _csrf(request)
    return Page(
        Stack(
            Text(f"Signed in as {username}"),
            Form(
                html.input(type="hidden", name="csrf_token", value=token),
                SubmitButton("Sign out"),
                action="/logout",
                method="post",
            ),
        ),
        title="Home",
    )


@app.action("/logout", method="POST")
def logout(request: Request) -> RedirectResponse:
    request.session.clear()
    return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
