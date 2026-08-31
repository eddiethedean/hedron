# Notes list tutorial (create, list, delete)

Build a small notes workspace with `DataWorkspace.with_screen`. This tutorial covers
**create, list, and edit** surfaces (delete stays disabled unless you supply destructive
policy). Prefer this facade over hand-wiring list/detail routes.

Paste into a new project after the [quickstart](../getting-started/quickstart.md), or use
`hedron new NAME --template crud`.

## Prerequisites

- [Build your first app](../getting-started/quickstart.md) (`@app.page` + view refresh)
- Optional: [Minimal form](../guides/minimal-form.md) for Advanced explicit `Form` / CSRF

## Golden path — `DataWorkspace.with_screen`

```python title="app.py"
import os

from pydantic import BaseModel, Field

from hedron import DesignSystem, Hedron, Stack, Text
from hedron_data import DataWorkspace, DataWorkspacePolicy, InMemoryDataSource

design = DesignSystem.brand("notes", accent="#2563eb")

app = Hedron(
    title="Notes",
    security="standard",
    explorer="off",
    theme=design,
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)


class Note(BaseModel):
    id: str
    body: str = Field(min_length=1, max_length=500)


# In-memory only — replace with an authorized durable DataEditorSource in production.
_SOURCE = InMemoryDataSource(
    [{"id": "1", "body": "Ship the docs demo"}],
    key_field="id",
    writable_fields=frozenset({"body"}),
)

notes = DataWorkspace(
    name="notes",
    model=Note,
    source=_SOURCE,
    policy=DataWorkspacePolicy(
        can_read=lambda: True,
        can_create=lambda: True,
        can_edit=lambda: True,
    ),
).with_screen(path="/notes", title="Notes")
app.include(notes)


class QuickNote(BaseModel):
    message: str = Field(min_length=1, max_length=200)


@app.action("/quick-note", method="POST", fallback="/")
def add_quick_note(data: QuickNote):
    return Text(data.message)


@app.page("/", title="Home")
def home():
    return Stack(
        Text("Open /notes for the DataWorkspace screen."),
        Text("Production replacements: persistence, authorization, transactions."),
        add_quick_note.form(),
    )
```

Install `hedron[data]` (or `hedron-data`) when running outside a scaffold that already
declares it.

## Run

```bash
python -m pip install "hedron[data]>=1.0.0" "uvicorn[standard]"
uvicorn app:app --reload
```

Open [http://127.0.0.1:8000/notes](http://127.0.0.1:8000/notes).

## What it shows

- `DataWorkspace.with_screen` for list/detail/create/edit composition
- `@app.action` for a validated side form on the home page
- `DesignSystem.brand` as the ordinary theme input

## Pattern warm-ups (simulated)

Docs simulations for CSRF, HTMX fragment POST, and list refresh — no server required.
These Advanced explicit `@app.page` listings match the Demo tabs; prefer the golden path
above for new apps.

### Try CSRF form POST (simulated)

=== "Demo"

    Classic POST — confirmation replaces the notes region. Docs simulation.

    <!-- hedron-sim:minimal-form -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    import os
    from datetime import datetime, timezone

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


    @app.view("/status")
    def status():
        stamp = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
        return html.div(
            Text(f"All systems operational · refreshed {stamp}"),
            role="status",
            aria={"live": "polite"},
        )


    @app.view("/notes-count")
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

### Try HTMX mutation (simulated)

=== "Demo"

    HTMX fragment POST — submit swaps the declared result region. Docs simulation.

    <!-- hedron-sim:mutations-htmx -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    from __future__ import annotations

    import os
    from typing import Annotated

    from fastapi import Form, Request

    from hedron import Hedron, Page, Stack, SubmitButton, Text, TextInput, html
    from hedron.security import csrf_token_for_request

    app = Hedron(
        title="Mutations HTMX",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    result = app.region("save-result", description="Save result")


    def _csrf(request: Request) -> str:
        return csrf_token_for_request(request, request.app.state.hedron_security)


    @app.page("/")
    def home(request: Request) -> Page:
        token = _csrf(request)
        return Page(
            Stack(
                html.form(
                    html.input(type="hidden", name="csrf_token", value=token),
                    TextInput(name="note", value="Ship the docs demo"),
                    SubmitButton("Save"),
                    method="post",
                    **{
                        "hx-post": "/save",
                        "hx-target": result.selector,
                        "hx-swap": "innerHTML",
                    },
                ),
                html.div(id=result.id, role="status", aria={"live": "polite"}),
            ),
            title="Mutations",
        )


    @app.action("/save", method="POST", fragment_regions=(result,))
    def save(note: Annotated[str, Form()] = "") -> object:
        return html.div(html.strong("Saved in region"), Text(note))
    ```

## Try the finished notes app (simulated)

=== "Demo"

    Miniature list — add multiple notes, then delete any row. Docs simulation.

    <!-- hedron-sim:crud-notes -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    from __future__ import annotations

    import os
    from typing import Annotated
    from uuid import uuid4

    from fastapi import Form, Request

    from hedron import CsrfField, Hedron, Page, Stack, SubmitButton, Text, TextInput, html

    app = Hedron(
        title="CRUD notes",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "replace-in-production"),
    )

    NOTES: dict[str, str] = {}
    listing = app.region("notes-list", description="Notes list")


    def render_list(request: Request):
        del request  # request kept for signature parity with fragment handlers
        if not NOTES:
            return html.div(Text("No notes yet."), id=listing.id)
        items = []
        for note_id, body in NOTES.items():
            items.append(
                html.li(
                    Text(body),
                    " ",
                    html.form(
                        CsrfField(),
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
        return Page(
            Stack(
                render_list(request),
                html.form(
                    CsrfField(),
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


    @app.action("/notes", method="POST", fragment_regions=(listing,))
    def add_note(request: Request, note: Annotated[str, Form()] = "") -> object:
        text = note.strip()
        if text:
            NOTES[str(uuid4())] = text
        return render_list(request)


    @app.action("/notes/delete", method="POST", fragment_regions=(listing,))
    def delete_note(request: Request, note_id: Annotated[str, Form()] = "") -> object:
        NOTES.pop(note_id, None)
        return render_list(request)
    ```

## Scaffold (intentional Path C)

This tutorial **replaces** the generated `app.py` with a complete notes app. That is
deliberate — not the golden-path “edit the Hello string” flow.

```bash
python -m pip install "hedron>=1.0.0" "uvicorn[standard]"
python -m hedron new crud-notes
cd crud-notes
python -m pip install -e .
```

Replace the generated `app.py` with the complete example below.

## Complete `app.py`

```python
from __future__ import annotations

from typing import Annotated
from uuid import uuid4

from pydantic import BaseModel, Field

from hedron import Control, Form, FormBody, Hedron, Page, Stack, SubmitButton, Text, html, refresh

app = Hedron(
    title="CRUD notes",
    security="standard",
    session_secret="replace-in-production",
)

NOTES: dict[str, str] = {}


class NoteIn(BaseModel):
    body: Annotated[str, Field(min_length=1), Control(label="Note")]


class DeleteNote(BaseModel):
    note_id: str


@app.view("/notes")
def notes():
    if not NOTES:
        items = [html.li(Text("No notes yet."))]
    else:
        items = [
            html.li(
                Text(body),
                Form(
                    html.input(type="hidden", name="note_id", value=note_id),
                    SubmitButton("Delete"),
                    action=delete,
                    style="display:inline",
                ),
            )
            for note_id, body in NOTES.items()
        ]
    return html.ul(*items, id="notes-list")


@app.action("/notes", method="POST", fallback="/")
def create_note(data: Annotated[NoteIn, FormBody()]):
    text = data.body.strip()
    if text:
        NOTES[str(uuid4())] = text
    return refresh(notes)


@app.action("/notes/delete", method="POST", fallback="/")
def delete(data: Annotated[DeleteNote, FormBody()]):
    NOTES.pop(data.note_id, None)
    return refresh(notes)


@app.page("/")
def home() -> Page:
    return Page(
        Stack(Text("Notes"), create_note.form(submit_label="Add"), notes()),
        title="Notes",
    )
```

## Run and verify

```bash
uvicorn app:app --reload
```

1. Open <http://127.0.0.1:8000/>
2. Add a note — the notes view refreshes without a full navigation
3. Delete a note — the same view updates
4. (Optional) Follow [Add update](#add-update) and edit a note in place

## Add update

Add a third command that writes a new body and refreshes the same view:

```python
class UpdateNote(BaseModel):
    note_id: str
    body: Annotated[str, Field(min_length=1), Control(label="Note")]


@app.action("/notes/update", method="POST", fallback="/")
def update_note(data: Annotated[UpdateNote, FormBody()]):
    text = data.body.strip()
    if data.note_id in NOTES and text:
        NOTES[data.note_id] = text
    return refresh(notes)
```

Render `update_note.form(value=UpdateNote(note_id=note_id, body=body), submit_label="Save")`
inside each row, or keep an explicit `Form(action=update_note)` with hidden `note_id`.

For a fuller admin surface (auth + create/update/delete on users), see the
[reference app walkthrough](reference-app.md).

## What you practiced

| Concept | Where |
|---|---|
| Replaceable list | `@app.view` / `notes()` |
| Actions | `@app.action` + `refresh(notes)` |
| Generated form | `create_note.form()` (`FormBody`) |
| Per-row delete | `Form(action=delete)` |

## Next

- Persist rows (SQLAlchemy / your ORM) instead of the module-level `NOTES` dict —
  [Notes + SQLAlchemy](notes-sqlalchemy.md) (create/list/delete)
- Gate routes with [Authentication](../guides/authentication.md)
- Study the full [reference app](reference-app.md) for sessions, multi-worker jobs, and packaging
- [Live interaction](../guides/live-interaction.md) for poll / stream / SSE

## Advanced — explicit `@app.page` / handles

When you eject or need full `Page` control, lower to `@app.page`, `@app.view`, and
`@app.action` with explicit `FormBody` / regions. See [DATA.md](../api/DATA.md) and the
[reference app](reference-app.md) for authenticated create/update/delete admin patterns.

## Next

- [Jobs poll](jobs-poll.md) (`TaskFlow`) · [Session auth](session-auth.md)
  (`SessionAuthFlow`) · [Dashboards](../guides/dashboards.md) (`DashboardWorkspace`)
