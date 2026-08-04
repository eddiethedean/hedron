# Minimal form POST

Submit a classic HTML form with CSRF, without HTMX fragments or validation
machinery. Use this after [HTMX interactions](htmx-interactions.md) (GET refresh)
and before the full [Forms and actions](forms-and-actions.md) deep dive.

## What you will build

A page with a note field. Submitting POSTs to an action and returns a confirmation
page. The GET seeds the CSRF cookie; the form posts the matching token.

```python title="app.py"
from fastapi import Form, Request

from hedron import Hedron, Page, Stack, SubmitButton, Text, TextInput, html
from hedron.security import csrf_token_for_request

app = Hedron(
    title="Notes",
    security="standard",
    session_secret="replace-in-production",
)


@app.page("/")
def home(request: Request) -> Page:
    token = csrf_token_for_request(request, request.app.state.hedron_security)
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

```bash
uv run uvicorn app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000), type a note, and submit.
Without a matching `csrf_token`, the POST returns `403`.

## What this teaches

| Piece | Role |
|---|---|
| GET page | Seeds the `hedron_csrf` cookie via the security profile |
| Hidden `csrf_token` | Same value the cookie holds for this session |
| `@app.action(..., method="POST")` | Mutation route; CSRF validated automatically under `security="standard"` |
| FastAPI `Form(...)` | Ordinary request parsing—no Hedron-specific body type required |

## Next steps

- Add HTMX targets, validation fragments, and `InteractionResult` in
  [Forms and actions](forms-and-actions.md).
- Gate routes with sessions in [Authentication](authentication.md).
- CSRF profiles and headers: [Security](security.md).
