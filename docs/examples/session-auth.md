# Session auth

Minimal session login gate with CSRF. Demo credentials only — replace before any deploy.

### Try it (simulated)

=== "Demo"

    Wrong password → 401. ada / correct-horse → signed-in panel. Docs simulation.

    <!-- hedron-sim:auth-login -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
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
    ```

## Run without cloning the monorepo

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: py -3 -m venv .venv && .\.venv\Scripts\Activate.ps1
pip install "hedron>=0.23.0,<0.24" "uvicorn[standard]"
# Copy https://raw.githubusercontent.com/eddiethedean/hedron/main/examples/session-auth/app.py → app.py
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
