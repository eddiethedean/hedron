# Session auth

Bounded session login with `SessionAuthFlow`. Demo credentials only — replace before any
deploy. Hedron is **not** an identity provider.

### Try it (simulated)

=== "Demo"

    Wrong password → soft redirect to /login?error=1. ada / correct-horse → signed-in panel. Docs simulation.

    <!-- hedron-sim:auth-login -->

=== "Code"

    Real recipe listing with the documented soft redirect and logout flow. The Demo tab is a simplified view:

    ```python title="app.py"
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


    @app.command("/login", fallback="/login")
    def login(
        request: Request,
        username: str = FastAPIForm(...),
        password: str = FastAPIForm(...),
    ):
        if USERS.get(username) != password:
            return RedirectResponse("/login?error=1", status_code=status.HTTP_303_SEE_OTHER)
        request.session["username"] = username
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


    @app.command("/logout", fallback="/login")
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
    ```

## Run without cloning the monorepo

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: py -3 -m venv .venv && .\.venv\Scripts\Activate.ps1
pip install "hedron>=0.60.0,<0.61" "uvicorn[standard]"
curl -fsSL https://raw.githubusercontent.com/eddiethedean/hedron/main/examples/session-auth/app.py -o app.py
uvicorn app:app --reload
```

## Run (monorepo)

```bash
uv sync
uv run uvicorn app:app --app-dir examples/session-auth --reload
```

Open [http://127.0.0.1:8000/login](http://127.0.0.1:8000/login). Demo: `ada` / `correct-horse`.

## What it shows

- `SessionAuthFlow` login/logout composition around explicit `authenticate` callbacks
- Required `RateLimitPolicy` and session rotation policy
- Application-owned credential check (not an IdP)

## Advanced — explicit `@app.page` / Form

Lower to `@app.page("/login")`, `@app.command`, `CsrfField`, and manual redirects when
ejecting. See [AUTH.md](../api/AUTH.md) and [Authentication](../guides/authentication.md).

Source: [`examples/session-auth`](https://github.com/eddiethedean/hedron/tree/main/examples/session-auth).
