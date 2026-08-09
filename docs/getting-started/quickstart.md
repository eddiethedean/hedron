# Build your first app

**~5–10 minutes** from a clean environment to **Hello from hedron new**, a working
**Refresh** click, then a one-line edit. Prefer **`python -m hedron`** so PATH never
matters.

## Prerequisites

- CPython **3.11–3.14** — verify with `python3 --version` (Windows: `py -3 --version`)
- Use a **clean virtual environment** for your first try. Supported pins (CI-proven):
  FastAPI `>=0.141.1,<0.142`, Pydantic `>=2.13.4,<2.14` (declared Pydantic range is
  wider — see [Compatibility](../COMPATIBILITY.md)). Shared envs often resolve the wrong
  FastAPI/Pydantic.
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

!!! tip "Pip needs two installs"

    With **pip**, install Hedron once for the **CLI**, then again with `pip install -e .`
    inside the scaffold so uvicorn uses the project pin. The **uv** path below does this
    in one flow. See
    [FAQ](../guides/faq.md#why-install-hedron-twice-cli-then-project).

Pin production installs with `hedron>=0.23.0,<0.24`.

=== "uv (recommended)"

    ```bash
    # macOS / Linux
    uvx --from "hedron>=0.23.0,<0.24" hedron new my-hedron-app
    cd my-hedron-app
    uv sync
    uv run uvicorn app:app --reload
    ```

    Windows (PowerShell), after installing uv:

    ```powershell
    uvx --from "hedron>=0.23.0,<0.24" hedron new my-hedron-app
    cd my-hedron-app
    uv sync
    uv run uvicorn app:app --reload
    ```

=== "pip (venv)"

    1. **CLI:** `pip install "hedron>=0.23.0,<0.24" "uvicorn[standard]"` (provides `hedron` / `python -m hedron`)
    2. **Project:** after `hedron new`, `cd` into the app and `pip install -e .` (uvicorn uses the scaffold pin)

    ```bash
    # macOS / Linux
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install "hedron>=0.23.0,<0.24" "uvicorn[standard]"
    python -m hedron new my-hedron-app
    cd my-hedron-app
    python -m pip install -e .
    uvicorn app:app --reload
    ```

    ```powershell
    # Windows (PowerShell)
    py -3 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install "hedron>=0.23.0,<0.24" "uvicorn[standard]"
    python -m hedron new my-hedron-app
    cd my-hedron-app
    python -m pip install -e .
    uvicorn app:app --reload
    ```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). You should see **Hello from hedron new**.

**Click Refresh status.** The panel text should update with a new UTC timestamp. Hedron
returns a small HTML fragment; [HTMX](https://htmx.org) swaps it into the declared region
— the interactive promise of the scaffold.

### If something fails

| Symptom | Fix |
|---|---|
| `hedron: command not found` | Use `python -m hedron …` (or finish the pip CLI install) |
| `ModuleNotFoundError: hedron` after `hedron new` | Run `pip install -e .` / `uv sync` **inside** the scaffold directory |
| FastAPI / dependency resolver errors | Use a **clean** venv; Hedron needs FastAPI `>=0.141.1,<0.142` |
| Port 8000 already in use | `uvicorn app:app --reload --port 8001` |
| Page loads but Refresh does nothing | Confirm HTMX static is mounted and the status region id matches; see [troubleshooting](../guides/troubleshooting.md) |

More: [FAQ](../guides/faq.md) · [Troubleshooting](../guides/troubleshooting.md).

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

## Alternative — add Hedron to an existing FastAPI app

!!! warning "FastAPI pin is a hard prerequisite"

    Hedron requires FastAPI `>=0.141.1,<0.142`. Shared or older FastAPI environments will
    fail to resolve. Use a **clean venv** (or upgrade FastAPI into that pin) before mounting.
    See [troubleshooting](../guides/troubleshooting.md).

If you already have a FastAPI project that satisfies the pin, install
`hedron>=0.23.0,<0.24` and **include a `HedronRouter`** (recommended). You own
session/security middleware — see the full listing in
[Plain FastAPI](../guides/plain-fastapi.md).

```python
from fastapi import FastAPI
from hedron import HedronRouter, Page, Text, mount_hedron_static

api = FastAPI()
mount_hedron_static(api)
ui = HedronRouter(prefix="/ui")


@ui.page("/")
def home() -> Page:
    return Page(Text("Hello from Hedron"), title="Home")


api.include_router(ui)
```

Alternate: mount a full `Hedron()` sub-app with `api.mount("/", ui)` when you want the
facade’s middleware — [Hedron API](../api/HEDRON.md) · [Mount](../api/MOUNT.md).

Prefer `hedron new` for the first-hour Refresh demo. Existing-app depth:
[Plain FastAPI](../guides/plain-fastapi.md).

## Alternative — manual `app.py` (no scaffold)

Prefer `hedron new` when you can. This pasteable file still includes the **Refresh**
demo so you see HTMX fragment swaps without the CLI scaffold.

```python title="app.py"
import os
from datetime import UTC, datetime

from hedron import Hedron, Page, RefreshButton, Stack, Text, html, swap

app = Hedron(
    title="Acme Console",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "replace-in-production"),
)

status = app.region("status", description="Status panel")


def status_panel() -> object:
    stamp = datetime.now(UTC).strftime("%H:%M:%S UTC")
    return html.div(
        Text(f"Status · {stamp}"),
        id=status.id,
        role="status",
        aria={"live": "polite"},
    )


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            Text("Hello from Hedron"),
            status_panel(),
            RefreshButton.for_region(status, href="/status", label="Refresh status"),
        ),
        title="Home",
    )


@app.fragment("/status", region=status)
def status_fragment() -> object:
    return swap(status_panel())
```

```bash
uvicorn app:app --reload   # or: uv run uvicorn app:app --reload
```

Open localhost, click **Refresh status**, and confirm the timestamp updates without a
full reload.

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
