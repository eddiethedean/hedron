# Build your first app

In this guide, you will render a complete page from typed Python components and observe
how the same route responds to an HTMX fragment request.

Complete [installation](installation.md) first so you have a project with `hedron` and
`uvicorn` (prefer `hedron new`).

**Next after this page:** [HTMX interactions](../guides/htmx-interactions.md) →
[Minimal form](../guides/minimal-form.md) → [Learning path](learning-path.md)

Pick **one** path below. Do not scaffold with `hedron new` and then also paste a new
`app.py` over it unless you intend to replace the scaffold.

## Path A — After `hedron new` (recommended)

If you already ran:

```bash
pip install "hedron>=0.10.1"
hedron new my-hedron-app
cd my-hedron-app
pip install -e .   # or: uv sync
```

the scaffold already created `app.py`. **Do not recreate it.** Skip to
[Run it](#2-run-it).

Open `app.py` only if you want to read or tweak the generated home page. The rest of this
guide (fragment check, CLI) works against that file as-is.

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

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). You should see the scaffold or
manual home page as a full HTML document. Hedron mounts its browser runtime, applies the
standard security policy, and includes a responsive default stylesheet. Override its
semantic CSS variables or add normal application CSS as your design evolves. If you want
an unstyled canvas instead, create the app with `Hedron(default_styles=False)`.

## 3. See fragment rendering

Ask the same endpoint for an HTMX response:

```bash
curl -H 'HX-Request: true' http://127.0.0.1:8000/
```

The response contains route content rather than a duplicate document shell. Hedron
chooses page or fragment rendering from explicit request headers; your route continues
to return the same typed component tree.

For a **browser click** that swaps a region (not only `curl`), continue to
[HTMX interactions](../guides/htmx-interactions.md).

## 4. Check the project

=== "uv"

    ```bash
    uv run hedron --app app:app check
    uv run hedron --app app:app routes
    ```

=== "Activated virtualenv (pip)"

    ```bash
    hedron --app app:app check
    hedron --app app:app routes
    ```

`check` reports configuration and compilation diagnostics with stable codes. `routes`
prints the registered route metadata as JSON, which is useful both to humans and CI.

!!! warning "Use a real session secret"

    The literal secret above is only for local development. Load a strong secret from
    your deployment environment and never commit a production value. See
    [configuration](../CONFIGURATION.md) for environment precedence and production
    gates.

## Where to go next

1. [HTMX interactions](../guides/htmx-interactions.md) — refresh a declared region in the browser
2. [Minimal form POST](../guides/minimal-form.md) — CSRF-safe classic form
3. [Learning path](learning-path.md) — full beginner → production order
4. [Core concepts](core-concepts.md) — why pages and fragments are separate modes
5. [Runnable examples](../examples/runnable.md) — real servers (not simulated gallery demos)
6. [Shipped APIs](../api/README.md)
