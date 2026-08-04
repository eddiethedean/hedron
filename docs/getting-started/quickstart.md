# Build your first app

In this guide, you will render a complete page from typed Python components and observe
how the same route responds to an HTMX fragment request.

Complete [installation](installation.md) first so `app.py` lives in a project with
`hedron` and `uvicorn` installed (or use `hedron new`).

## 1. Create the application

Create `app.py`:

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

=== "Activated virtualenv"

    ```bash
    uvicorn app:app --reload
    ```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Hedron renders a full HTML
document, mounts its browser runtime, applies the standard security policy, and includes
a responsive default stylesheet. Override its semantic CSS variables or add normal
application CSS as your design evolves. If you want an unstyled canvas instead, create
the app with `Hedron(default_styles=False)`.

## 3. See fragment rendering

Ask the same endpoint for an HTMX response:

```bash
curl -H 'HX-Request: true' http://127.0.0.1:8000/
```

The response contains route content rather than a duplicate document shell. Hedron
chooses page or fragment rendering from explicit request headers; your route continues
to return the same typed component tree.

## 4. Check the project

```bash
uv run hedron --app app:app check
uv run hedron --app app:app routes
```

`check` reports configuration and compilation diagnostics with stable codes. `routes`
prints the registered route metadata as JSON, which is useful both to humans and CI.

!!! warning "Use a real session secret"

    The literal secret above is only for local development. Load a strong secret from
    your deployment environment and never commit a production value. See
    [configuration](../CONFIGURATION.md) for environment precedence and production
    gates.

## Where to go next

- Follow the [learning path](learning-path.md).
- Build a targeted server update with [HTMX interactions](../guides/htmx-interactions.md).
- Submit a CSRF-safe form with [Minimal form POST](../guides/minimal-form.md).
- Learn why pages and fragments are separate render modes in [core concepts](core-concepts.md).
- Browse the [component gallery](../examples/gallery.md) (in-browser simulations) or clone the
  [reference app](../examples/reference-app.md).
- Browse [shipped APIs](../api/README.md).
