# Build your first app

In about five minutes, scaffold a Hedron app, run it, and confirm an HTMX fragment
update. You need CPython **3.11–3.14** and either
[`uv`](https://docs.astral.sh/uv/getting-started/installation/) or an activated virtual
environment. Node.js is not required.

If terms such as project folder, terminal, virtual environment, or development server are new,
use [Your first application with VS Code](first-app-vscode.md). In Posit Workbench, use the
[`hedron-posit` beginner walkthrough](first-app-posit-workbench.md).

## 1. Scaffold and run

=== "uv (recommended)"

    ```bash
    uvx --from "hedron>=0.41.0,<0.42" hedron new my-hedron-app
    cd my-hedron-app
    uv sync
    uv run uvicorn app:app --reload
    ```

=== "pip (activated virtual environment)"

    ```bash
    python -m pip install "hedron>=0.41.0,<0.42" "uvicorn[standard]"
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
| Open `/` | The page route returns a typed `Page` and Hedron renders a full document | The Hello page loads |
| Click **Refresh status** | HTMX requests `/status` for the declared region | Only the status timestamp changes |
| Send the wrong target | Hedron rejects a target outside the route’s region policy | The request fails closed with HTTP 403 |

That page/fragment distinction is the central Hedron interaction model. The next guide
lets you inspect it directly; you do not need to understand HTMX before completing this
quickstart.

## 2. Make one edit

Open `app.py` and change:

```python
Text("Hello from hedron new")
```

to:

```python
Text("Hello from Ada")
```

Save the file. Uvicorn reloads and the browser shows the new text.

## 3. Verify the project

```bash
python -m hedron --app app:app check
# uv users: uv run hedron --app app:app check
```

Informational findings on a development scaffold are normal. Errors include a
remediation and a `HED-*` diagnostic code.

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
and a `components/` directory. The generated page declares a region and returns a small
fragment for that region. See [Scaffold anatomy](core-concepts.md) or the
[single-file examples](../examples/single-file.md) when you want the complete source.

```text
my-hedron-app/
├── app.py           # application, page route, and status fragment
├── pyproject.toml   # dependencies and bounded Hedron pin
└── components/      # project-owned reusable UI components
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
