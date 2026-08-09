# Reference app walkthrough

Annotated tour of
[`examples/reference-app`](https://github.com/eddiethedean/hedron/tree/main/examples/reference-app)—
the FastAPI flagship CRUD sample on the **0.23.0** train.

Click through the core patterns below (docs simulations — no live server), then run the
full app locally.

## Auth gate (simulated)

The reference app gates the dashboard behind identity. Sign-in simulation:

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

## CSRF on forms (simulated)

Unsafe POSTs require a CSRF token. Missing token → 403:

=== "Demo"

    POST with CSRF succeeds; missing token → 403. Docs simulation.

    <!-- hedron-sim:csrf-guard -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
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
    ```

## Fragment list refresh (simulated)

Create/delete rows with HTMX swaps into a declared region — the same idea as the
user table on the dashboard:

=== "Demo"

    Fragment list refresh pattern used throughout the reference app. Docs simulation.

    <!-- hedron-sim:crud-notes -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    from __future__ import annotations

    import os
    from typing import Annotated
    from uuid import uuid4

    from fastapi import Form, Request

    from hedron import Hedron, Page, Stack, SubmitButton, Text, TextInput, html
    from hedron.security import csrf_token_for_request

    app = Hedron(
        title="CRUD notes",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "replace-in-production"),
    )

    NOTES: dict[str, str] = {}
    listing = app.region("notes-list", description="Notes list")


    def _csrf(request: Request) -> str:
        return csrf_token_for_request(request, request.app.state.hedron_security)


    def render_list(request: Request):
        token = _csrf(request)
        if not NOTES:
            return html.div(Text("No notes yet."), id=listing.id)
        items = []
        for note_id, body in NOTES.items():
            items.append(
                html.li(
                    Text(body),
                    " ",
                    html.form(
                        html.input(type="hidden", name="csrf_token", value=token),
                        html.input(type="hidden", name="note_id", value=note_id),
                        SubmitButton("Delete"),
                        method="post",
                        **{
                            "hx-post": "/notes/delete",
                            "hx-target": listing.selector,
                            "hx-swap": "outerHTML",
                        },
                    ),
                )
            )
        return html.div(html.ul(*items), id=listing.id)


    @app.page("/")
    def home(request: Request) -> Page:
        token = _csrf(request)
        return Page(
            Stack(
                render_list(request),
                html.form(
                    html.input(type="hidden", name="csrf_token", value=token),
                    TextInput(name="note", placeholder="New note"),
                    SubmitButton("Add note"),
                    method="post",
                    **{
                        "hx-post": "/notes",
                        "hx-target": listing.selector,
                        "hx-swap": "outerHTML",
                    },
                ),
            ),
            title="CRUD",
        )


    @app.component("/notes", methods=["POST"], fragment_regions=(listing,))
    def add_note(request: Request, note: Annotated[str, Form()] = "") -> object:
        text = note.strip()
        if text:
            NOTES[str(uuid4())] = text
        return render_list(request)


    @app.component("/notes/delete", methods=["POST"], fragment_regions=(listing,))
    def delete_note(request: Request, note_id: Annotated[str, Form()] = "") -> object:
        NOTES.pop(note_id, None)
        return render_list(request)
    ```

## Chart panel refresh (simulated)

Dashboard chart routes return `InteractionResult` fragments:

=== "Demo"

    Refresh advances a short chart sequence (then wraps). Docs simulation.

    <!-- hedron-sim:charts-htmx -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    import os

    from hedron import Hedron, InteractionResult, Page, Stack, html

    app = Hedron(
        title="Charts HTMX",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    panel = app.region("chart-panel", description="Chart panel")


    def chart_panel(label: str):
        return html.div(
            html.strong(label),
            html.span("Simple panel stand-in for a chart fragment."),
            id=panel.id,
            role="status",
        )


    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                chart_panel("Chart panel"),
                html.button(
                    "Refresh chart panel",
                    type="button",
                    **{
                        "hx-get": "/charts/refresh",
                        "hx-target": panel.selector,
                        "hx-swap": "outerHTML",
                    },
                ),
            ),
            title="Charts",
        )


    @app.component("/charts/refresh", fragment_regions=(panel,))
    def refresh() -> InteractionResult:
        return InteractionResult(
            content=chart_panel("Chart panel updated"),
            region_id=panel.id,
            trigger="chartRefreshed",
            cache="vary-htmx",
            explanation="Primary fragment refresh for chart panel",
        )
    ```

## Run

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
uv run uvicorn app:app --app-dir examples/reference-app --reload
```

Sign in with HTTP Basic: **`admin` / `secret`**.

## What the app demonstrates

| Concern | Where to look (`examples/reference-app/`) | Simulated above |
|---|---|---|
| `Hedron()` app + security profile | `app.py` → `build_hedron_app()` | — |
| Session/user gate | `require_user` + router `dependencies=[Depends(require_user)]` | Auth gate |
| CSRF on forms | `csrf_token_for_request` + hidden field / `hx-headers` in `_create_form` | CSRF on forms |
| Create user POST | `@users.action("", method="POST")` | Fragment list refresh |
| Fragment table refresh | `@users.component("/table")`, addressable `user_table` | Fragment list refresh |
| DataEditor / Auto / charts | dashboard sections and `/charts/*` routes | Chart panel refresh |
| Color mode | `ColorModeToggle` + preference cookie helpers | — |

## Suggested reading order in the code

1. `build_hedron_app()` — how the app is constructed and the build dir is prepared
2. `home` page handler — CSRF token issuance for the dashboard
3. `_create_form` — progressive form with HTMX target on `#user-table`
4. User create/update/delete actions — validation, store mutation, fragment returns
5. Chart routes — `InteractionResult` + declared fragment regions

## Related guides

- [Forms and actions](../guides/forms-and-actions.md)
- [Authentication](../guides/authentication.md)
- [HTMX interactions](../guides/htmx-interactions.md)
- [Charts and HTMX](../guides/charts-and-htmx.md)
- [Plain FastAPI + HedronRouter](../guides/plain-fastapi.md)
