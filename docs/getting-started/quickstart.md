# Build your first app

Verify that the scaffold (or a minimal manual page) renders in the browser, then peek at
how the same route responds to an HTMX fragment request.

Complete [installation](installation.md) first so you have a project with `hedron` and
`uvicorn` (prefer `hedron new`).

**Next after this page:** [HTMX interactions](../guides/htmx-interactions.md) →
[Minimal form](../guides/minimal-form.md) → [Learning path](learning-path.md)

Pick **one** path below. Do not scaffold with `hedron new` and then also paste a new
`app.py` over it unless you intend to replace the scaffold.

## Path A — Verify the scaffold (recommended)

If you already ran the [installation](installation.md) scaffold steps, `app.py` exists.
**Do not recreate it.** Skip to [Run it](#2-run-it).

Open `app.py` only if you want to read or tweak the generated home page. The fragment
check and CLI below work against that file as-is.

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

## 2. Run it

=== "uv"

    ```bash
    uv run uvicorn app:app --reload
    ```

=== "Activated virtualenv (pip)"

    ```bash
    uvicorn app:app --reload
    ```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

**Success:** you see page text **Hello from hedron new** (scaffold) or your Path B
heading/card content. If the page is blank, returns 404, or assets fail to load, see
[Troubleshooting](../guides/troubleshooting.md).

Hedron mounts its browser runtime, applies the standard security policy, and includes a
responsive default stylesheet. Override its semantic CSS variables or add normal
application CSS as your design evolves. For an unstyled canvas, create the app with
`Hedron(default_styles=False)`.

## 3. Optional: fragment response via curl

Ask the same endpoint for an HTMX response (optional — a browser click is more satisfying
in the next guide):

```bash
curl -H 'HX-Request: true' http://127.0.0.1:8000/
```

The response contains route content rather than a duplicate document shell. Hedron
chooses page or fragment rendering from explicit request headers; your route continues
to return the same typed component tree.

For a **browser click** that swaps a region, continue to
[HTMX interactions](../guides/htmx-interactions.md).

## 4. Optional: check the project

After you have a working page, inspect the loaded app (advisory findings are normal on a
hello-world scaffold — Django/Plotly notes apply only if you use those stacks):

=== "uv"

    ```bash
    uv run hedron check --app app:app
    ```

=== "Activated virtualenv (pip)"

    ```bash
    hedron check --app app:app
    # or: python -m hedron check --app app:app
    ```

`hedron check` reports registry and security findings. Prefer `--app` so diagnostics load
your module explicitly.

## What you learned

- A typed `Page` renders as a full HTML document.
- The same route can return fragment HTML when HTMX headers are present.
- The CLI can inspect the app without opening a browser.

**Next:** [HTMX interactions](../guides/htmx-interactions.md) — click a refresh button in
the browser.
