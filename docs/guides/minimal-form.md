# Minimal form POST

Submit a classic HTML form with CSRF, without HTMX fragments or validation
machinery. Use this after [HTMX interactions](htmx-interactions.md) (GET refresh)
and before choosing between `@action` and `@component` POST in
[Mutations](mutations.md). The full [Forms and actions](forms-and-actions.md)
deep dive covers validation fragments.

## What you will build

A **notes** page with a note field. Submitting POSTs to an action and returns a
confirmation page. The GET seeds the CSRF cookie; the form posts the matching token.

**If you used `hedron new` (or finished the HTMX guide):** keep the existing `Hedron(...)`
app and your `/` home route. Add the imports below, then add `/notes` and `/save` **beside**
the routes you already have. Do not create a second app file.

### 1. Add a CSRF helper and imports

```python
from fastapi import Form, Request

from hedron import (
    Page,
    Stack,
    SubmitButton,
    Text,
    TextInput,
    csrf_token_for_request,
    html,
)


def _csrf(request: Request) -> str:
    """One-liner so forms never touch ``request.app.state`` inline."""
    return csrf_token_for_request(request, request.app.state.hedron_security)
```

(Merge with imports already present; you only need each name once.)

### 2. Add `/notes` and `/save` below your existing routes

```python
@app.page("/notes")
def notes(request: Request) -> Page:
    token = _csrf(request)
    return Page(
        Stack(
            Text("Leave a note"),
            html.form(
                html.input(type="hidden", name="csrf_token", value=token),
                TextInput("note", value="", required=True),
                SubmitButton("Save"),
                action="/save",
                method="post",
            ),
        ),
        title="Notes",
    )


@app.action("/save", method="POST")
def save(note: str = Form(...)) -> Page:
    return Page(Text(f"Saved: {note}"), title="Saved")
```

Your scaffold `/` home (and any HTMX routes) keep working. Open
[http://127.0.0.1:8000/notes](http://127.0.0.1:8000/notes) for this lesson.

### Complete file (Path B / reference)

Use this only if you are starting a fresh manual `app.py` (not extending a scaffold):

```python title="app.py"
from fastapi import Form, Request

from hedron import Hedron, Page, Stack, SubmitButton, Text, TextInput, csrf_token_for_request, html

app = Hedron(
    title="Notes",
    security="standard",
    session_secret="replace-in-production",
)


def _csrf(request: Request) -> str:
    return csrf_token_for_request(request, request.app.state.hedron_security)


@app.page("/")
def home(request: Request) -> Page:
    token = _csrf(request)
    return Page(
        Stack(
            Text("Leave a note"),
            html.form(
                html.input(type="hidden", name="csrf_token", value=token),
                TextInput("note", value="", required=True),
                SubmitButton("Save"),
                action="/save",
                method="post",
            ),
        ),
        title="Notes",
    )


@app.action("/save", method="POST")
def save(note: str = Form(...)) -> Page:
    return Page(Text(f"Saved: {note}"), title="Saved")
```

Run it:

=== "uv"

    ```bash
    uv run uvicorn app:app --reload
    ```

=== "Activated virtualenv (pip)"

    ```bash
    uvicorn app:app --reload
    ```

Open the notes URL above (or `/` on Path B), type a note, and submit.
Without a matching `csrf_token`, the POST returns `403`.

## What this teaches

| Piece | Role |
|---|---|
| `_csrf(request)` | Local helper — hides `request.app.state.hedron_security` |
| GET page | Seeds the `hedron_csrf` cookie via the security profile |
| Hidden `csrf_token` | Same value the cookie holds for this session |
| `@app.action(..., method="POST")` | Mutation route; CSRF validated automatically under `security="standard"` |
| FastAPI `Form(...)` | Ordinary request parsing—no Hedron-specific body type required |

## Next steps

- Add HTMX targets, validation fragments, and `InteractionResult` in
  [Forms and actions](forms-and-actions.md).
- Gate routes with sessions in [Authentication](authentication.md).
- CSRF profiles and headers: [Security](security.md).
