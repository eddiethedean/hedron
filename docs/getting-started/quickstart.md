# Build your first app

**~5–10 minutes** from a clean environment to **Hello from hedron new**, a working
**Refresh** click, then a one-line edit. Prefer **`python -m hedron`** so PATH never
matters.

## Prerequisites

- CPython **3.11–3.14** (use a **clean virtual environment** for your first try)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended) or `pip`
- No Node.js required

=== "Install uv (recommended)"

    ```bash
    # macOS / Linux
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Windows (PowerShell): irm https://astral.sh/uv/install.ps1 | iex
    # Or: brew install uv / see https://docs.astral.sh/uv/getting-started/installation/
    ```

=== "pip only"

    Use `python3` (macOS/Linux) or `py -3` (Windows) if `python` is missing or points at
    the wrong interpreter. Create a venv before installing.

## 1. Scaffold, sync, run

=== "uv (recommended)"

    ```bash
    uvx --from "hedron>=0.20.0,<0.21" hedron new my-hedron-app
    cd my-hedron-app
    uv sync
    uv run uvicorn app:app --reload
    ```

!!! note "Install pin"

    Pin `hedron>=0.20.0,<0.21` for the current published train.

=== "pip (venv)"

    Two installs — do both:

    1. **CLI:** `pip install "hedron>=0.20.0,<0.21" "uvicorn[standard]"` (provides `hedron` / `python -m hedron`)
    2. **Project:** after `hedron new`, `cd` into the app and `pip install -e .` (uvicorn uses the scaffold pin)

    ```bash
    python3 -m venv .venv          # Windows: py -3 -m venv .venv
    source .venv/bin/activate      # Windows PowerShell: .\.venv\Scripts\Activate.ps1
    python -m pip install "hedron>=0.20.0,<0.21" "uvicorn[standard]"
    python -m hedron new my-hedron-app
    cd my-hedron-app
    python -m pip install -e .     # project-local pinned hedron for uvicorn
    uvicorn app:app --reload
    ```

!!! tip "Why does pip install twice?"

    Step 1 provides the **CLI**. Step 2 installs the scaffold’s **project dependency** so
    uvicorn uses the pinned version. See
    [FAQ](../guides/faq.md#why-install-hedron-twice-cli-then-project).

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). You should see **Hello from hedron new**.

**Click Refresh status.** The panel text should update with a new UTC timestamp. Hedron
returns a small HTML fragment; [HTMX](https://htmx.org) swaps it into the declared region
— the interactive promise of the scaffold.

=== "Demo"

    Same fragment swap as the scaffold — docs simulation (no server).

    <!-- hedron-sim:hello-refresh-quickstart -->

=== "Code"

    What `hedron new` writes as `app.py` (the real app, not the docs simulator):

    ```python title="app.py"
    import os
    from datetime import UTC, datetime

    from hedron import Hedron, Page, RefreshButton, Stack, Text, html, swap

    app = Hedron(
        title="Hedron App",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "replace-in-production"),
    )

    status = app.region("service-status", description="Live status panel")


    def status_panel():
        stamp = datetime.now(UTC).strftime("%H:%M:%S UTC")
        return html.div(
            Text(f"All systems operational · refreshed {stamp}"),
            id=status.id,
            role="status",
            aria={"live": "polite"},
        )


    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                Text("Hello from hedron new"),
                status_panel(),
                RefreshButton.for_region(status, href="/status", label="Refresh status"),
            ),
            title="Home",
        )


    @app.fragment("/status", region=status)
    def refresh_status():
        return swap(status_panel())
    ```

Extras, Flask/Django, and troubleshooting: [Installation](installation.md).

## 2. What the scaffold looks like

`hedron new` writes the `app.py` shown in the **Code** tab above (timestamp line may
vary). Keep that file open while you edit — the Demo tab is only a docs simulation.

## 3. Edit the Hello text (~2 minutes)

**Do not** re-run `hedron new` or paste a second `app.py` over the scaffold unless you
intend to replace it.

1. Change the home `Text("Hello from hedron new")` to your name.
2. Save — with `--reload`, the browser should update.
3. Extend the same Refresh pattern: [HTMX interactions](../guides/htmx-interactions.md).
4. Then add a small form: [Minimal form POST](../guides/minimal-form.md).

```python
# Before
Text("Hello from hedron new")

# After
Text("Hello from Ada")
```

Optional check:

```bash
# --app is a global flag (before the subcommand)
python -m hedron --app app:app check
# or: uv run hedron --app app:app check
```

Advisory findings on a hello-world scaffold are normal.

## Alternative — manual `app.py` (no scaffold)

!!! warning "Static Hello only"

    This path skips `hedron new` and does **not** include Refresh / HTMX. Prefer the
    scaffold above for the interactive first-hour experience. Continue to
    [HTMX interactions](../guides/htmx-interactions.md) after you switch to a scaffolded
    app (or add a region yourself).

Use this only if you did **not** use `hedron new`. Create a project directory, install
`hedron>=0.20.0,<0.21` and `uvicorn[standard]`, then save:

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

Set `session_secret` from the environment in real apps — see
[Configuration](../CONFIGURATION.md). More pasteable variants:
[single-file examples](../examples/single-file.md).

`Hedron` is a FastAPI application — DI, lifespan, middleware, and JSON routes remain
available. Always set an explicit `session_secret` before deployment.

## What you learned

- A typed `Page` renders as a full HTML document.
- A declared `region` + `@app.fragment` updates part of the page without a full reload.
- Editing Python components updates the UI (with reload).

**Next:** [HTMX interactions](../guides/htmx-interactions.md) →
[Minimal form POST](../guides/minimal-form.md) → [Learning path](learning-path.md)
