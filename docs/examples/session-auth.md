# Session auth

Minimal session login gate with CSRF. Demo credentials only — replace before any deploy.

### Try it (simulated)

=== "Demo"

    Simplified login panel simulation (wrong password → error; ada / correct-horse →
    signed-in). The real recipe uses soft redirects and a logout form — see Code.

    <!-- hedron-sim:auth-login -->

=== "Code"

    Real recipe — same as the curl download below (`/login`, soft redirect from `/`,
    logout POST). Demo tab is a simplified simulation only.

    ```python title="app.py"
    """Session login gate (demo credentials). Local learning only."""

    from __future__ import annotations

    from fastapi import Form as FastAPIForm
    from fastapi import Request, status
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


    def _csrf(request: Request) -> str:
        return csrf_token_for_request(request, request.app.state.hedron_security)


    @app.page("/login")
    def login_page(request: Request) -> Page | RedirectResponse:
        if request.session.get("username"):
            return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
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
            return RedirectResponse("/login?error=1", status_code=status.HTTP_303_SEE_OTHER)
        request.session["username"] = username
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


    @app.page("/")
    def home(request: Request) -> Page | RedirectResponse:
        username = request.session.get("username")
        if not username:
            # Soft landing — redirect to login instead of a bare 401.
            return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
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
    ```

## Run without cloning the monorepo

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: py -3 -m venv .venv && .\.venv\Scripts\Activate.ps1
pip install "hedron>=0.25.0,<0.26" "uvicorn[standard]"
curl -fsSL https://raw.githubusercontent.com/eddiethedean/hedron/main/examples/session-auth/app.py -o app.py
uvicorn app:app --reload
```

## Run (monorepo)

```bash
uv sync
uv run uvicorn app:app --app-dir examples/session-auth --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) — unauthenticated visits **redirect to
`/login`**. Sign in with `ada` / `correct-horse`.

## What it shows

- Starlette session cookie via `Hedron(session_secret=...)`
- Soft landing redirect (not a bare 401) when `/` is unauthenticated
- CSRF-safe login and logout POSTs

Source: [`examples/session-auth`](https://github.com/eddiethedean/hedron/tree/main/examples/session-auth).
Full narrative: [Authentication](../guides/authentication.md).
