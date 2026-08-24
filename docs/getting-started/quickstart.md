---
description: Scaffold, run, edit, and verify your first Hedron application in about ten minutes.
search:
  boost: 2
---

# Build your first app

About 10 minutes after Python **3.11–3.14** and either
[`uv`](https://docs.astral.sh/uv/getting-started/installation/) or an activated virtual
environment. Node.js is not required.

If terms such as project folder, terminal, virtual environment, or development server are new,
use [Your first application with VS Code](first-app-vscode.md). In Posit Workbench, use the
[`hedron-posit` beginner walkthrough](first-app-posit-workbench.md).

Install from PyPI: `hedron>=0.62.0,<0.63`. Other pins and extras:
[Installation](installation.md).

## You will learn

- how `hedron new` creates an ordinary Python application;
- how a component screen becomes a complete HTML page;
- how `@app.refreshable` returns a targeted HTML fragment;
- how to make one edit, run a diagnostic check, and choose the next tutorial step.

You do not need prior HTMX or JavaScript knowledge. The [core concepts](core-concepts.md)
page explains the model after you have seen it work.

## 1. Scaffold and run

=== "uv (recommended)"

    ```bash
    uvx --from "hedron>=0.62.0,<0.63" hedron new my-hedron-app
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
    python -m pip install "hedron>=0.62.0,<0.63" "uvicorn[standard]"
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
from datetime import UTC, datetime

from hedron import Hedron, Stack, Text, html

app = Hedron(
    title="Hedron App",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "replace-in-production"),
)


@app.refreshable("/status")
def status():
    stamp = datetime.now(UTC).strftime("%H:%M:%S UTC")
    return html.div(
        Text(f"All systems operational · refreshed {stamp}"),
        role="status",
        aria={"live": "polite"},
    )


@app.command(fallback="/")
def ping():
    from hedron import refresh

    return refresh(status).toast("Refreshed")


@app.screen("/", title="Home")
def home():
    return Stack(
        Text("Hello from hedron new"),
        status(),
        status.refresh_button("Refresh status"),
        ping.button("Ping"),
    )
```

Prefer `@app.screen` for new apps. Use explicit `Page` + `@app.page` only when you need
full `Page` constructor control — see the [Hedron API](../api/HEDRON.md).

Change:

```python
Text("Hello from hedron new")
```

to:

```python
Text("Hello from Ada")
```

Save the file. Uvicorn reloads and the browser shows the new text.

## Optional: form command with validation

For forms, prefer `@app.form_command` (discovers one Pydantic model and lowers to
`FormBody` + `@app.command`):

```python
from pydantic import BaseModel, Field

class QuickNote(BaseModel):
    message: str = Field(min_length=1, max_length=200)

@app.form_command("/notes", fallback="/", success="Saved note")
def add_note(data: QuickNote):
    return Text(data.message)

# Inside home(): add_note.form()
```

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

`hedron new` writes an ordinary `app.py` and a `pyproject.toml` with a bounded Hedron pin.
The project configuration reserves `components/` as the component root; create that
directory when you add your first project-owned component. The generated page declares a
refreshable view and returns a small fragment for that view.

```text
my-hedron-app/
├── app.py           # application, screen, command, and refreshable view
└── pyproject.toml   # dependencies and bounded Hedron pin

# Created later when you add project-owned components:
components/
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
