# CRUD tutorial

Build a small in-memory notes list with CSRF and HTMX fragment updates. Paste this into
a new project after the [quickstart](../getting-started/quickstart.md). For the larger
reference application (auth, charts, extras), see the
[reference app walkthrough](reference-app.md).

## Prerequisites

- [Minimal form](../guides/minimal-form.md) (CSRF basics)
- [Mutations](../guides/mutations.md) (`@component` POST vs `@action`)

## Scaffold

```bash
pip install "hedron>=0.10.0"
hedron new crud-notes
cd crud-notes
pip install -e .
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
from hedron.security import csrf_token_for_request

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

## What you practiced

| Concept | Where |
|---|---|
| CSRF cookie + form field | `_csrf` / hidden `csrf_token` |
| Fragment allowlist | `fragment_regions=(LIST,)` |
| Mutation decorator | `@component(..., methods=["POST"])` — see [Mutations](../guides/mutations.md) |
| `InteractionResult` | Create/delete handlers |

## Next

- Persist rows (SQLAlchemy / your ORM) instead of the module-level `NOTES` dict
- Gate routes with [Authentication](../guides/authentication.md)
- Study the full [reference app](reference-app.md) for sessions, charts, and packaging
- [Live interaction](../guides/live-interaction.md) for poll / stream / SSE
