---
description: Scaffold, run, edit, and verify your first Hedron application in about ten minutes.
search:
  boost: 2
---

# Build your first app

About 10 minutes after Python **3.10–3.14** and either
[`uv`](https://docs.astral.sh/uv/getting-started/installation/) or an activated virtual
environment. Node.js is not required.

If terms such as project folder, terminal, virtual environment, or development server are new,
use [Your first application with VS Code](first-app-vscode.md). In Posit Workbench, use the
[`hedron-posit` beginner walkthrough](first-app-posit-workbench.md).

Install from PyPI: `hedron>=1.0.0` is the compatibility floor. For a new application,
prefer the current bounded range `hedron>=1.0.7,<1.1`; use `hedron==1.0.7` when you
need an exact reproducible environment. For a higher-level application API, start with
[Edron](edron-quickstart.md). Other pins and extras: [Installation](installation.md).

## You will learn

- how `hedron new` creates an ordinary Python application;
- how a returned component tree becomes a complete HTML page;
- how `@app.view` returns a targeted HTML fragment handle;
- how to make one edit, run a diagnostic check, and choose the next tutorial step.

You do not need prior HTMX or JavaScript knowledge. The [core concepts](core-concepts.md)
page explains the model after you have seen it work.

## 1. Scaffold and run

=== "uv (recommended)"

    ```bash
    uvx --from "hedron>=1.0.0" hedron new my-hedron-app
    cd my-hedron-app
    uv sync
    uv run uvicorn app:app --reload
    ```

=== "pip (activated virtual environment)"

    Create and activate a **new empty** virtual environment first (`python3 -m venv .venv`
    then `source .venv/bin/activate`, or on Windows `py -3 -m venv .venv` and
    `.\.venv\Scripts\Activate.ps1`). If PowerShell blocks scripts, use
    `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or `activate.bat`.

    ```bash
    python -m pip install "hedron>=1.0.0" "uvicorn[standard]"
    python -m hedron new my-hedron-app
    cd my-hedron-app
    python -m pip install -e .
    uvicorn app:app --reload
    ```

The second pip install installs the generated project and its declared Hedron pin.
The `uv` path performs the equivalent step through `uv sync`.

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). You should see **Hello from
hedron new**.

Click **Refresh status**. The timestamp should change without a full-page reload. That
confirms the browser requested `/status`, Hedron authorized the declared target, and
HTMX replaced only the status region.

### What just happened?

| Browser action | Server behavior | Visible result |
|---|---|---|
| Open `/` | The page route returns a `Page` and Hedron renders a full document | The Hello page loads |
| Click **Refresh status** | HTMX requests `/status` for the declared region | Only the status timestamp changes |
| Send the wrong target | Hedron rejects a target outside the route’s region policy | The request fails closed with HTTP 403 |

That page/fragment distinction is the central Hedron interaction model. The next guide
lets you inspect it directly; you do not need to understand HTMX before completing this
quickstart.

## 2. Make one edit

The generated `app.py` looks like this (you can paste it if scaffold is unavailable):

```python
import os
from datetime import datetime, timezone

from hedron import Hedron, Stack, Text, ToastHost, html

app = Hedron(
    title="Hedron App",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "replace-in-production"),
)


@app.view("/status")
def status():
    stamp = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    return html.div(
        Text(f"All systems operational · refreshed {stamp}"),
        role="status",
        aria={"live": "polite"},
    )


@app.action("/ping", fallback="/")
def ping():
    from hedron import refresh

    return refresh(status).toast("Refreshed")


@app.page("/")
def home():
    return Stack(
        Text("Hello from hedron new"),
        status(),
        status.refresh_button("Refresh status"),
        ping.button("Ping"),
        ToastHost(),
    )
```

The canonical 1.0 roles are `@app.page`, `@app.view`, and `@app.action`; see the
[Hedron API](../api/HEDRON.md).

Change:

```python
Text("Hello from hedron new")
```

to:

```python
Text("Hello from Ada")
```

Save the file. Uvicorn reloads and the browser shows the new text.

## Optional: typed action form with validation

For forms, keep validation in the typed action boundary with `FormBody` and explicit controls.

```python
from typing import Annotated

from pydantic import BaseModel, Field
from hedron import FormBody

class QuickNote(BaseModel):
    message: str = Field(min_length=1, max_length=200)

@app.action("/notes", fallback="/")
def add_note(data: Annotated[QuickNote, FormBody()]):
    return Text(data.message)

# Inside the Stack returned by home():
# add_note.form(submit_label="Add note")
```

Add that final expression as another child of the existing `Stack`, restart if necessary,
and reload the page. Hedron renders the model-derived field, includes the CSRF boundary, and
returns validation errors through the form. For persistence and an explicit refresh target,
continue to [Build a notes app](../examples/build-notes-app.md).

Scaffolds: `hedron new NAME --template crud` (also shows `DataWorkspace.with_screen`).

## 3. Verify the project

```bash
python -m hedron --app app:app check
# uv users: uv run hedron --app app:app check
```

Informational findings on a development scaffold are normal. Errors include a
remediation and a `HED-*` diagnostic code (see [Error codes](../guides/error-codes.md)).

## If something fails

| Symptom | Fix |
|---|---|
| `hedron: command not found` | Use `python -m hedron`, or use the `uvx` command above |
| `ModuleNotFoundError: hedron` | Run `uv sync` or `python -m pip install -e .` inside the generated directory |
| Resolver conflict | Start in a clean environment; see [Compatibility](../COMPATIBILITY.md) |
| Port 8000 is busy | Add `--port 8001` and open that port |
| Refresh does nothing | See [HTMX troubleshooting](../guides/troubleshooting.md#htmx-403-on-fragment-request) |

For Python installation, Windows commands, optional extras, proxies, and adapters, use
[Installation](installation.md).

## What was generated?

`hedron new` writes an ordinary `app.py`, a `pyproject.toml` with a bounded Hedron pin,
and an empty `components/` directory for project-owned components. The generated page
declares a canonical view and returns a small fragment for that view.

```text
my-hedron-app/
├── app.py           # application, page, action, and view handlers
├── pyproject.toml   # dependencies and bounded Hedron pin
└── components/      # empty component root, ready for project components
```

These are normal Python project files. Hedron does not generate a separate JavaScript
application or require Node.js for the production build.

## Continue

| If you want to… | Continue with |
|---|---|
| Understand the refresh you just used | [What is HTMX?](what-is-htmx.md) |
| Add another independently updating region | [HTMX interactions](../guides/htmx-interactions.md) |
| Submit data safely | [Minimal form POST](../guides/minimal-form.md) |
| See the full beginner-to-production sequence | [Learning path](learning-path.md) |

The recommended next project is [Build a notes app](../examples/build-notes-app.md),
which carries this same application through a form, persistence, authentication, and
deployment checks.
