# Build your first app

**~5–10 minutes** from a clean environment to **Hello from hedron new**, then a
one-line edit. Prefer **`python -m hedron`** so PATH never matters.

!!! note "Why install twice?"

    The first `pip install` / `uvx` provides the **CLI**. After `hedron new`,
    `pip install -e .` / `uv sync` installs the scaffold’s **project dependency** so
    uvicorn uses the pinned version. See
    [FAQ](../guides/faq.md#why-install-hedron-twice-cli-then-project).

## 1. Install and run the scaffold

=== "pip (venv — recommended)"

    ```bash
    python -m venv .venv
    source .venv/bin/activate   # Windows PowerShell: .\.venv\Scripts\Activate.ps1
    python -m pip install "hedron>=0.15.0" "uvicorn[standard]"
    python -m hedron new my-hedron-app
    cd my-hedron-app
    python -m pip install -e .   # project-local pinned hedron for uvicorn
    uvicorn app:app --reload
    ```

=== "uv (recommended CLI)"

    ```bash
    uvx --from "hedron>=0.15.0" hedron new my-hedron-app
    cd my-hedron-app
    uv sync
    uv run uvicorn app:app --reload
    ```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). You should see **Hello from hedron new**.

Extras, Flask/Django, and troubleshooting: [Installation](installation.md).

## 2. Edit the scaffold (~2 minutes)

**Do not** re-run `hedron new` or paste a second `app.py` over the scaffold unless you
intend to replace it.

1. Open `app.py` and change the home `Text(...)` (or greeting string) to your name.
2. Save — with `--reload`, the browser should update.
3. Continue to [HTMX interactions](../guides/htmx-interactions.md) for a button that
   updates one region without a full page reload.

Optional checks:

```bash
curl -H 'HX-Request: true' http://127.0.0.1:8000/
python -m hedron check --app app:app   # or: uv run hedron check --app app:app
```

Advisory findings on a hello-world scaffold are normal.

## Alternative — manual `app.py` (no scaffold)

Use this only if you did **not** use `hedron new`. Create a project directory, install
`hedron>=0.15.0` and `uvicorn[standard]`, then save:

```python title="app.py"
from hedron import Card, Heading, Hedron, Page, Stack, Text

app = Hedron(
    title="Acme Console",
    security="standard",
    session_secret="replace-in-production",
)


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            Heading("Acme Console", level=1),
            Card(Text("Everything on this page came from Python components.")),
        ),
        title="Home",
    )
```

```bash
uvicorn app:app --reload   # or: uv run uvicorn app:app --reload
```

More pasteable variants: [single-file examples](../examples/single-file.md).

`Hedron` is a FastAPI application — DI, lifespan, middleware, and JSON routes remain
available. Always set an explicit `session_secret` before deployment.

## What you learned

- A typed `Page` renders as a full HTML document.
- Editing Python components updates the UI (with reload).
- The same route can return fragment HTML when HTMX headers are present.

**Next:** [HTMX interactions](../guides/htmx-interactions.md) →
[Minimal form](../guides/minimal-form.md) → [Learning path](learning-path.md)
