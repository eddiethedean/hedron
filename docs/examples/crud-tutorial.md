# Notes list tutorial (create, list, delete)

Build a small in-memory notes list with CSRF and HTMX fragment updates. This tutorial
covers **create, list, and delete** — add [update](#add-update) below, or use the
[reference app](reference-app.md) for authenticated create/**update**/delete admin.

Paste into a new project after the [quickstart](../getting-started/quickstart.md).

## Prerequisites

- [Minimal form](../guides/minimal-form.md) (CSRF basics)
- [Mutations](../guides/mutations.md) (`@component` POST vs `@action`)

Warm up with the two prerequisite patterns (docs simulations — no server):

### Try CSRF form POST (simulated)

=== "Demo"

    Classic POST — confirmation replaces the notes region. Docs simulation.

    <!-- hedron-sim:minimal-form -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    import os

    from fastapi import Form as FastAPIForm

    from hedron import (
        CsrfField,
        Form,
        Hedron,
        Page,
        RefreshButton,
        Stack,
        SubmitButton,
        Text,
        TextInput,
        html,
        redirect_local,
        swap,
    )

    app = Hedron(
        title="Notes",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    notes_region = app.region("notes-count", description="Notes counter")
    _NOTES: list[str] = []


    def notes_panel():
        return html.div(
            Text(f"Notes saved: {len(_NOTES)}"),
            id=notes_region.id,
            role="status",
            aria={"live": "polite"},
        )


    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                notes_panel(),
                RefreshButton.for_region(
                    notes_region, href="/notes-count", label="Refresh notes count"
                ),
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


    @app.fragment("/notes-count", region=notes_region)
    def refresh_notes_count():
        return swap(notes_panel())


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


    @app.component("/save", methods=["POST"], fragment_regions=(result,))
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

## Scaffold (intentional Path C)

This tutorial **replaces** the generated `app.py` with a complete notes app. That is
deliberate — not the golden-path “edit the Hello string” flow.

```bash
python -m pip install "hedron>=0.36.0,<0.37" "uvicorn[standard]"
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

from fastapi import Form, Request

from hedron import (
    FragmentRegion,
    Hedron,
    InteractionResult,
    Page,
    Stack,
    SubmitButton,
    Text,
    TextInput,
    html,
)
from hedron import csrf_token_for_request

app = Hedron(
    title="CRUD notes",
    security="standard",
    session_secret="replace-in-production",
)

NOTES: dict[str, str] = {}
LIST = FragmentRegion(id="notes-list", selector="#notes-list")


def _csrf(request: Request) -> str:
    return csrf_token_for_request(request, request.app.state.hedron_security)


def render_list(request: Request) -> object:
    token = _csrf(request)
    if not NOTES:
        return Text("No notes yet.")
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
                        "hx-target": LIST.selector,
                        "hx-swap": "innerHTML",
                    },
                ),
            )
        )
    return html.ul(*items)


@app.page("/")
def home(request: Request) -> Page:
    token = _csrf(request)
    return Page(
        Stack(
            Text("Notes"),
            html.div(render_list(request), id=LIST.id),
            html.form(
                html.input(type="hidden", name="csrf_token", value=token),
                TextInput("body", value="", required=True),
                SubmitButton("Add"),
                method="post",
                **{
                    "hx-post": "/notes",
                    "hx-target": LIST.selector,
                    "hx-swap": "innerHTML",
                },
            ),
        ),
        title="Notes",
    )


@app.component("/notes", methods=["POST"], fragment_regions=(LIST,))
def create_note(
    request: Request,
    body: Annotated[str, Form()],
) -> InteractionResult:
    text = body.strip()
    if text:
        NOTES[str(uuid4())] = text
    return InteractionResult(
        content=render_list(request),
        region_id=LIST.id,
        explanation="Append a note and refresh the list",
    )


@app.component("/notes/delete", methods=["POST"], fragment_regions=(LIST,))
def delete_note(
    request: Request,
    note_id: Annotated[str, Form()],
) -> InteractionResult:
    NOTES.pop(note_id, None)
    return InteractionResult(
        content=render_list(request),
        region_id=LIST.id,
        explanation="Delete a note and refresh the list",
    )
```

## Run and verify

```bash
uvicorn app:app --reload
```

1. Open <http://127.0.0.1:8000/>
2. Add a note — `#notes-list` swaps without a full navigation
3. Delete a note — the same region updates
4. (Optional) Follow [Add update](#add-update) and edit a note in place

## Add update

Extend `render_list` so each row can POST a new body, then add a handler:

```python
# Inside the per-note <li>, after the body Text(...):
html.form(
    html.input(type="hidden", name="csrf_token", value=token),
    html.input(type="hidden", name="note_id", value=note_id),
    TextInput("body", value=body, required=True),
    SubmitButton("Save"),
    method="post",
    **{
        "hx-post": "/notes/update",
        "hx-target": LIST.selector,
        "hx-swap": "innerHTML",
    },
),

@app.component("/notes/update", methods=["POST"], fragment_regions=(LIST,))
def update_note(
    request: Request,
    note_id: Annotated[str, Form()],
    body: Annotated[str, Form()],
) -> InteractionResult:
    text = body.strip()
    if note_id in NOTES and text:
        NOTES[note_id] = text
    return InteractionResult(
        content=render_list(request),
        region_id=LIST.id,
        explanation="Update a note and refresh the list",
    )
```

For a fuller admin surface (auth + create/update/delete on users), see the
[reference app walkthrough](reference-app.md).

## What you practiced

| Concept | Where |
|---|---|
| CSRF cookie + form field | `_csrf` / hidden `csrf_token` |
| Fragment allowlist | `fragment_regions=(LIST,)` |
| Mutation decorator | `@component(..., methods=["POST"])` — see [Mutations](../guides/mutations.md) |
| `InteractionResult` | Create/delete (and optional update) handlers |

## Next

- Persist rows (SQLAlchemy / your ORM) instead of the module-level `NOTES` dict —
  [Notes + SQLAlchemy](notes-sqlalchemy.md) (create/list/delete)
- Gate routes with [Authentication](../guides/authentication.md)
- Study the full [reference app](reference-app.md) for sessions, multi-worker jobs, and packaging
- [Live interaction](../guides/live-interaction.md) for poll / stream / SSE
