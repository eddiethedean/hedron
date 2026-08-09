# Build your first app

**~5–10 minutes after Python 3.11+ and uv/pip are ready** to **Hello from hedron new**,
a working **Refresh** click, then a one-line edit. Prefer **`python -m hedron`** so PATH
never matters. Cold machines (install Python/uv first) or Codespaces first boot often take
longer — see [Try with Codespaces](../examples/try-it.md).

This page is the golden path only (`hedron new` → Refresh → edit). After Hello works,
read [What is HTMX?](what-is-htmx.md). Adding Hedron to an existing FastAPI app:
[Existing / plain FastAPI](../guides/plain-fastapi.md). Pasteable variants without the
CLI: [single-file examples](../examples/single-file.md).

## Prerequisites

- CPython **3.11–3.14** — verify with `python3 --version` (Windows: `py -3 --version`)
- Use a **clean virtual environment** for your first try (shared envs often resolve the
  wrong FastAPI/Pydantic). Exact Supported vs declared ranges:
  [Compatibility](../COMPATIBILITY.md).
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

!!! warning "Pip needs two installs — skip the second and imports fail"

    With **pip**, install Hedron once for the **CLI**, then again with `pip install -e .`
    inside the scaffold so uvicorn uses the project pin. Forgetting the second step causes
    `ModuleNotFoundError: hedron`. The **uv** path below does this in one flow. See
    [FAQ](../guides/faq.md#why-install-hedron-twice-cli-then-project).

Pin production installs with `hedron>=0.25.0,<0.26`.

=== "uv (recommended)"

    ```bash
    # macOS / Linux
    uvx --from "hedron>=0.25.0,<0.26" hedron new my-hedron-app
    cd my-hedron-app
    uv sync
    uv run uvicorn app:app --reload
    ```

    Windows (PowerShell), after installing uv:

    ```powershell
    uvx --from "hedron>=0.25.0,<0.26" hedron new my-hedron-app
    cd my-hedron-app
    uv sync
    uv run uvicorn app:app --reload
    ```

=== "pip (venv)"

    1. **CLI:** `pip install "hedron>=0.25.0,<0.26" "uvicorn[standard]"` (provides `hedron` / `python -m hedron`)
    2. **Project:** after `hedron new`, `cd` into the app and `pip install -e .` (uvicorn uses the scaffold pin)

    ```bash
    # macOS / Linux
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install "hedron>=0.25.0,<0.26" "uvicorn[standard]"
    python -m hedron new my-hedron-app
    cd my-hedron-app
    python -m pip install -e .
    uvicorn app:app --reload
    ```

    ```powershell
    # Windows (PowerShell)
    py -3 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install "hedron>=0.25.0,<0.26" "uvicorn[standard]"
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
| FastAPI / dependency resolver errors | Use a **clean** venv; prefer Supported FastAPI `>=0.141.1,<0.142` ([Compatibility](../COMPATIBILITY.md)) |
| Port 8000 already in use | `uvicorn app:app --reload --port 8001` |
| Page loads but Refresh does nothing | Confirm HTMX static is mounted and the status region id matches; see [troubleshooting](../guides/troubleshooting.md) |

More: [FAQ](../guides/faq.md) · [Troubleshooting](../guides/troubleshooting.md).

Extras, Flask/Django, and troubleshooting: [Installation](installation.md).

## 2. What the scaffold looks like

`hedron new` writes `app.py` (timestamp line may vary). Keep that file open while you
edit. `security="standard"` and `session_secret` are scaffold defaults so CSRF-safe forms
work later; replace the secret before any deploy ([Configuration](../CONFIGURATION.md)).

### Preview (no server)

Optional docs simulation of the same fragment swap — **not** a substitute for running
uvicorn above. Use it only after you have seen Hello on localhost, or if you are
browsing docs offline. The **Code** tab is the scaffold listing.

=== "Demo"

    Optional preview — docs simulation (no server). Run uvicorn above first.

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


## 3. Edit the Hello text (~2 minutes)

**Do not** re-run `hedron new` or paste a second `app.py` over the scaffold unless you
intend to replace it.

1. Change the home `Text("Hello from hedron new")` to your name.
2. Save — with `--reload`, the browser should update.
3. Optionally skim [What is HTMX?](what-is-htmx.md), then extend the same Refresh pattern:
   [HTMX interactions](../guides/htmx-interactions.md).
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

## Other paths (not the golden path)

| If you… | Go here |
|---|---|
| Already have a FastAPI app | [Existing / plain FastAPI](../guides/plain-fastapi.md) |
| Want a pasteable file without `hedron new` | [Single-file examples](../examples/single-file.md) |
| Need extras / adapters / install troubleshooting | [Installation](installation.md) |

## What you learned

- A typed `Page` renders as a full HTML document.
- A declared `region` + `@app.fragment` updates part of the page without a full reload.
- Editing Python components updates the UI (with reload).

**Next:** [What is HTMX?](what-is-htmx.md) →
[HTMX interactions](../guides/htmx-interactions.md) →
[Minimal form POST](../guides/minimal-form.md) → [Learning path](learning-path.md)
