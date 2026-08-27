"""Session login gate (demo credentials). Local learning only."""

from __future__ import annotations

from fastapi import Form as FastAPIForm
from fastapi import Request, status
from fastapi.responses import RedirectResponse

from hedron import (
    Alert,
    CsrfField,
    Form,
    Hedron,
    Page,
    Stack,
    SubmitButton,
    Text,
    TextInput,
)

app = Hedron(
    title="Session auth demo",
    security="standard",
    explorer="off",
    session_secret="replace-in-production",
)

# Demo only — never hard-code production passwords.
USERS = {"ada": "correct-horse"}


@app.action("/login", fallback="/login")
def login(
    request: Request,
    username: str = FastAPIForm(...),
    password: str = FastAPIForm(...),
):
    if USERS.get(username) != password:
        return RedirectResponse("/login?error=1", status_code=status.HTTP_303_SEE_OTHER)
    request.session["username"] = username
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@app.action("/logout", fallback="/login")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)


@app.page("/login")
def login_page(request: Request, error: str | None = None) -> Page | RedirectResponse:
    if request.session.get("username"):
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    feedback = (
        Alert("Invalid username or password.", tone="danger", title="Sign-in failed")
        if error == "1"
        else None
    )
    return Page(
        Stack(
            Text("Sign in (demo: ada / correct-horse)"),
            feedback,
            Form(
                CsrfField(),
                TextInput("username", value="", required=True),
                TextInput("password", value="", type="password", required=True),
                SubmitButton("Sign in"),
                action=login,
            ),
        ),
        title="Login",
    )


@app.page("/")
def home(request: Request) -> Page | RedirectResponse:
    username = request.session.get("username")
    if not username:
        # Soft landing — redirect to login instead of a bare 401.
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    return Page(
        Stack(
            Text(f"Signed in as {username}"),
            logout.button("Sign out"),
        ),
        title="Home",
    )
