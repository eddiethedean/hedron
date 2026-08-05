# Build your first app

Complete [installation](installation.md) first so you have a project with `hedron` and
`uvicorn` (prefer `hedron new`).

**Next after this page:** [HTMX interactions](../guides/htmx-interactions.md) →
[Minimal form](../guides/minimal-form.md) → [Learning path](learning-path.md)

Pick **one** path below. Do not scaffold with `hedron new` and then also paste a new
`app.py` over it unless you intend to replace the scaffold.

## Path A — Edit the scaffold (recommended)

If you already finished [installation](installation.md), the app is running and you see
**Hello from hedron new**. **Do not recreate `app.py` or re-run uvicorn as the main job
of this page.**

**Do this instead (~2 minutes):**

1. Open `app.py` and change the home `Text(...)` (or greeting string) to your name.
2. Save — with `--reload`, the browser should update.
3. Continue to [HTMX interactions](../guides/htmx-interactions.md) for a button that
   updates one region without a full page reload.

Optional checks (after the edit works):

```bash
curl -H 'HX-Request: true' http://127.0.0.1:8000/
```

```bash
python -m hedron check --app app:app   # or: uv run hedron check --app app:app
```

Advisory findings on a hello-world scaffold are normal.

## Path B — Manual `app.py`

Use this only if you did **not** use `hedron new`. Create `app.py`:

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

`Hedron` is a FastAPI application, so FastAPI dependency injection, lifespan hooks,
middleware, and JSON routes remain available. `@app.page` adds the contract that this
route returns a navigable HTML document. Always set an explicit `session_secret` before
deployment.

### Run it (Path B only)

=== "uv"

    ```bash
    uv run uvicorn app:app --reload
    ```

=== "Activated virtualenv (pip)"

    ```bash
    uvicorn app:app --reload
    ```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

**Success:** you see your Path B heading/card content. If the page is blank, returns 404,
or assets fail to load, see [Troubleshooting](../guides/troubleshooting.md).

Hedron mounts its browser runtime, applies the standard security policy, and includes a
responsive default stylesheet. For an unstyled canvas, create the app with
`Hedron(default_styles=False)`.

## What you learned

- A typed `Page` renders as a full HTML document.
- Editing Python components updates the UI (with reload).
- The same route can return fragment HTML when HTMX headers are present.

**Next:** [HTMX interactions](../guides/htmx-interactions.md) — click a refresh button in
the browser.
