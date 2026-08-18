# Minimal form POST

Add a CSRF-safe note form to the **same** FastAPI scaffold from
[HTMX interactions](htmx-interactions.md). Submitting appends to `_NOTES` and
redirects home so **Notes saved: N** updates. Use this before choosing between
`@action` and `@component` POST in [Mutations](mutations.md). The full
[Forms and actions](forms-and-actions.md) deep dive covers validation fragments.

!!! note "FastAPI field name"

    FastAPI/Flask hidden field is **`csrf_token`** via `CsrfField()`. Django middleware
    requires **`csrfmiddlewaretoken`** and does not accept the portable name.

## What you will build

A note field on the home page (next to the notes counter). POST `/save` appends the
note, then `redirect_local("/")` reloads the page so the count increments. CSRF uses
`CsrfField()` — FastAPI page renders seed the token automatically.

### Try it (simulated)

=== "Demo"

    Classic POST — confirmation replaces the notes region. Docs simulation.

    <!-- hedron-sim:minimal-form -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    import os
    from datetime import UTC, datetime

    from fastapi import Form as FastAPIForm

    from hedron import (
        CsrfField,
        Form,
        Hedron,
        Page,
        Stack,
        SubmitButton,
        Text,
        TextInput,
        html,
        redirect_local,
    )

    app = Hedron(
        title="Notes",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    _NOTES: list[str] = []


    @app.refreshable("/status")
    def status():
        stamp = datetime.now(UTC).strftime("%H:%M:%S UTC")
        return html.div(
            Text(f"All systems operational · refreshed {stamp}"),
            role="status",
            aria={"live": "polite"},
        )


    @app.refreshable("/notes-count")
    def notes():
        return html.div(
            Text(f"Notes saved: {len(_NOTES)}"),
            role="status",
            aria={"live": "polite"},
        )


    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                status(),
                status.refresh_button("Refresh status"),
                notes(),
                notes.refresh_button("Refresh notes count"),
                Text("Leave a note"),
                Form(
                    CsrfField(),
                    TextInput("note", value="Ship the docs demo", required=True),
                    SubmitButton("Save"),
                    action="/save",
                    method="post",
                ),
            ),
            title="Notes",
        )


    @app.action("/save", method="POST")
    def save(note: str = FastAPIForm(...)):
        text = note.strip()
        if text:
            _NOTES.append(text)
        return redirect_local("/")
    ```

**If you used `hedron new` (or finished the HTMX guide):** keep the existing `Hedron(...)`
app, `status`, `_NOTES`, and `notes`. Add the imports and routes below
**beside** what you already have. Do not create a second app file.

### 1. Add form imports

```python
from fastapi import Form as FastAPIForm

from hedron import (
    CsrfField,
    Form,
    Page,
    Stack,
    SubmitButton,
    Text,
    TextInput,
    html,
    redirect_local,
)
```

(Merge with imports already present; you only need each name once. Alias FastAPI’s
`Form` so it does not clash with Hedron’s `Form` component.)

### 2. Put the form on `home()` and add `/save`

Replace your `home()` from the HTMX guide with this (keep `status` /
`notes` as you already have them):

```python
@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            Text("Hello from hedron new"),
            status(),
            status.refresh_button("Refresh status"),
            notes(),
            notes.refresh_button("Refresh notes count"),
            Text("Leave a note"),
            Form(
                CsrfField(),
                TextInput("note", value="", required=True),
                SubmitButton("Save"),
                action="/save",
                method="post",
            ),
        ),
        title="Home",
    )


@app.action("/save", method="POST")
def save(note: str = FastAPIForm(...)):
    text = note.strip()
    if text:
        _NOTES.append(text)
    return redirect_local("/")
```

`CsrfField()` reads the token from the page `RenderContext` (seeded when
`security="standard"`). No manual `csrf_token_for_request` helper is required for this
path.

Reload, type a note, click **Save**. You return to `/` with **Notes saved: 1** (then 2,
…). Click **Refresh notes count** anytime — the fragment shows the same length.

Without a matching CSRF token, the POST returns `403`.

### Complete file (Path B / reference)

Use this only if you are starting a fresh manual `app.py` (not extending a scaffold).
Copy the **Code** tab above — it is the same refreshable + form app.

Run it:

=== "uv"

    ```bash
    uv run uvicorn app:app --reload
    ```

=== "Activated virtualenv (pip)"

    ```bash
    uvicorn app:app --reload
    ```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000), submit a note, and confirm the
count increments.

## Advanced: manual token seeding

Prefer `CsrfField()` on FastAPI pages. If you are porting an existing app that already
calls `csrf_token_for_request`, you can still pass an explicit token:

```python
from fastapi import Request

from hedron import CsrfField, csrf_token_for_request

def notes(request: Request) -> Page:
    token = csrf_token_for_request(request, request.app.state.hedron_security)
    return Page(
        Form(
            CsrfField(token=token),
            TextInput("note", value="", required=True),
            SubmitButton("Save"),
            action="/save",
            method="post",
        ),
        title="Notes",
    )
```

Raw `html.input(type="hidden", name="csrf_token", value=token)` remains valid but is
no longer the recommended golden-path pattern — see
[CSRF composition](../api/CSRF_COMPOSITION.md).

## What this teaches

| Piece | Role |
|---|---|
| `CsrfField()` | Hidden CSRF input from page `RenderContext` |
| GET page | Seeds the CSRF cookie / context via the security profile |
| `@app.action(..., method="POST")` | Mutation route; CSRF validated under `security="standard"` |
| `_NOTES.append(...)` | Same in-memory list the HTMX notes region reads |
| `redirect_local("/")` | Safe local redirect so the full page (and count) refresh |
| FastAPI `Form(...)` (aliased) | Ordinary request parsing — no Hedron-specific body type |

## Next steps

1. Pick a second-hour recipe: [Notes + SQLAlchemy](../examples/notes-sqlalchemy.md) or
   [Session auth](../examples/session-auth.md).
2. Or continue the golden path: [Learning path](../getting-started/learning-path.md).
3. Depth when you need it: [Forms and actions](forms-and-actions.md) ·
   [Mutations](mutations.md) · [Authentication](authentication.md) ·
   [Security](security.md) · [CSRF composition](../api/CSRF_COMPOSITION.md).
