# Notes + SQLAlchemy

Minimal FastAPI + Hedron notes app with SQLite persistence and CSRF-safe POST.
Supports **create, list, and delete** — not a full admin CRUD surface.

### Try it (simulated)

=== "Demo"

    Same list pattern as the notes recipe — add and delete rows. Docs simulation (in-memory; the real recipe uses SQLAlchemy + SQLite).

    <!-- hedron-sim:crud-notes -->

=== "Code"

    In-memory listing that reproduces the demo. The runnable recipe downloaded below replaces the list with SQLAlchemy + SQLite persistence:

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

## Run without cloning the monorepo

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: py -3 -m venv .venv && .\.venv\Scripts\Activate.ps1
pip install "hedron>=0.25.0,<0.26" "uvicorn[standard]" "sqlalchemy>=2.0"
curl -fsSL https://raw.githubusercontent.com/eddiethedean/hedron/main/examples/notes-sqlalchemy/app.py -o app.py
uvicorn app:app --reload
```

## Run (monorepo)

```bash
uv sync
uv run uvicorn app:app --app-dir examples/notes-sqlalchemy --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Notes persist in `notes.db` in the
process working directory (gitignored).

## What it shows

- `@app.page` + `@app.component` (POST) with a small `_csrf(request)` helper
- SQLAlchemy ORM + SQLite
- Post-Redirect-Get after save / delete

Source: [`examples/notes-sqlalchemy`](https://github.com/eddiethedean/hedron/tree/main/examples/notes-sqlalchemy).
Related: [Minimal form](../guides/minimal-form.md) · [Data apps](../guides/data-apps.md) ·
[Recipes](recipes/index.md).
