# Installation

Prerequisites, extras, host adapters, and troubleshooting.

**Do not start here for Hello.** The golden-path copy-paste lives on
[Build your first app](quickstart.md) (`hedron new` → Hello → Refresh). Use this page
for version checks, optional extras, Flask/Django adapters, and install failures.

Session secrets and `[tool.hedron]` keys: [Configuration](../CONFIGURATION.md).

## Prerequisites

- CPython **3.11–3.14** (use a **clean virtual environment** for your first try)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended) or `pip`
- No Node.js required

=== "Install uv"

    ```bash
    # macOS / Linux
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Windows (PowerShell): irm https://astral.sh/uv/install.ps1 | iex
    # Then reopen the shell and confirm: uv --version
    ```

=== "python vs python3"

    Prefer `python3` on macOS/Linux and `py -3` on Windows when `python` is missing or
    points at the wrong interpreter. Prefer **`python -m hedron`** so PATH never matters.

## Verify

After following [Build your first app](quickstart.md):

=== "uv"

    ```bash
    uv run python -c "import hedron; print(hedron.__version__)"
    ```

=== "pip (activated venv)"

    ```bash
    python -c "import hedron; print(hedron.__version__)"
    ```

Expect **`0.20.0`** (or a newer `0.20.x` patch) on this train / `main`. Last published
PyPI/git is **`v0.18.0`** until `v0.20.0` is cut. Pin with `hedron>=0.20.0,<0.21` for
production.

If `hedron` is not found after install, prefer **`python -m hedron …`** or see
[Troubleshooting](../guides/troubleshooting.md#hedron-command-not-found).

## Common install problems

| Symptom | Fix |
|---|---|
| `hedron: command not found` | Use `python -m hedron …`, `uvx --from "hedron>=0.20.0,<0.21" …`, or see [FAQ](../guides/faq.md#hedron-command-not-found) / [Troubleshooting](../guides/troubleshooting.md#hedron-command-not-found) |
| `ModuleNotFoundError: hedron` | Same interpreter as uvicorn; activate the venv, then `pip install -e .` / `uv sync` — [Troubleshooting](../guides/troubleshooting.md#wrong-interpreter-or-modulenotfounderror-for-hedron) |
| FastAPI / pip resolver conflict | Empty venv recommended; see [pin conflicts](../COMPATIBILITY.md#dependency-pin-conflicts) and [Troubleshooting](../guides/troubleshooting.md#fastapi-version-conflict-on-install) |
| `uv add` / “No pyproject.toml” | Create a project first, or use `hedron new` ([FAQ](../guides/faq.md#uv-add-hedron-failed-with-no-pyprojecttoml)) |
| Wrong / old version | `pip install -U "hedron>=0.20.0,<0.21"` — [Troubleshooting](../guides/troubleshooting.md#wrong-or-unexpected-version) |
| CSRF 403 on first POST | Seed cookie with a GET — [Troubleshooting](../guides/troubleshooting.md#csrf-403-on-post-fastapi-flask) |
| Cannot import DataTable / charts | Install extras — [Troubleshooting](../guides/troubleshooting.md#cannot-import-auto-datatable-chart-helpers) |
| Explorer 404 | Install `hedron[dev]` and enable development Explorer — [Troubleshooting](../guides/troubleshooting.md#explorer-404-or-missing-in-production) |
| Production missing manifest | Run `hedron build` before `HEDRON_ENV=production` — [Troubleshooting](../guides/troubleshooting.md#production-startup-missing-manifest-hed-build-0003) |

Full list: [Troubleshooting](../guides/troubleshooting.md) ·
[Failure gallery](../guides/troubleshooting.md#failure-gallery-top-5) ·
[FAQ](../guides/faq.md).

!!! tip "If install fails on FastAPI/Pydantic"

    Prefer a **clean virtual environment** for your first app (do not reuse a shared env
    that already pins an older FastAPI). Then see
    [Dependency pin conflicts](../COMPATIBILITY.md#dependency-pin-conflicts) for the
    Supported vs declared FastAPI/Pydantic ranges.

## Optional extras

Install extras only when you need them:

| Extra | When you need it | Package docs |
|---|---|---|
| `hedron[data]` | DataTable / DataEditor / data sources | [hedron-data](../packages/hedron-data.md) |
| `hedron[charts]` | LineChart and visualization adapters (Alpha) | [hedron-charts](../packages/hedron-charts.md) |
| `hedron[jinja]` | Optional HDJ (`.hdj`) templates | [hedron-jinja](../packages/hedron-jinja.md) |
| `hedron[dev]` | Component Explorer (`/hedron-explorer/`) | [hedron-explorer](../packages/hedron-explorer.md) |
| `hedron[conformance]` | Language-neutral conformance kit / CLI runner | [hedron-conformance](../packages/hedron-conformance.md) |
| `hedron[native]` | Optional Rust HTML-escape acceleration (Alpha) | [hedron-native](../packages/hedron-native.md) |
| `hedron[extras]` | Curated extras / workbenches | [hedron-extras](../packages/hedron-extras.md) |
| `hedron[notebook]` | Alpha server-side notebook preview | [hedron-notebook](../packages/hedron-notebook.md) |
| `hedron[mcp]` | Alpha deny-by-default MCP projection | [hedron-mcp](../packages/hedron-mcp.md) |
| `hedron[gradio]` | Alpha Gradio client interop (experimental) | [hedron-gradio](../packages/hedron-gradio.md) |
| `hedron[otel]` | Optional OpenTelemetry tracing helpers | — |
| `hedron[markdown]` / `[code]` / `[images]` / `[email]` / `[sanitize]` / `[auth]` / `[browser]` | Content, Authlib, or test helpers | — |

Also install directly (no flagship extra):
[hedron-sample-kit](../packages/hedron-sample-kit.md) ·
[hedron-sim](../packages/hedron-sim.md).
Full catalog: [Optional packages](../packages/index.md).

```bash
pip install "hedron[data]>=0.20.0,<0.21"          # example
pip install "hedron[charts]>=0.1.0,<0.2"         # Alpha — pin and expect churn
pip install "hedron-charts[plotly]>=0.1.0,<0.2"  # chart backend after charts extra (tip: 0.1.5)
```

### Other hosts

| Package | Use when |
|---|---|
| `hedron-flask` | Flask — `init_app` / Blueprint, page + fragment routing/HTMX Supported |
| `hedron-django` | Django `>=5.2,<6` — forms bridge + QuerySet DataSource Supported |
| `hedron-core` | Framework-neutral rendering only |

Quickstarts: [Flask](flask.md) · [Django](django.md).

### Component Explorer

With `hedron[dev]` installed and `explorer="development"` on `Hedron(...)`, open
[`/hedron-explorer/`](http://127.0.0.1:8000/hedron-explorer/) while the app is running.
Leave Explorer off in production.

## Alternative: manual project

Use this only if you are **not** using `hedron new`.

=== "uv"

    ```bash
    uv init my-hedron-app
    cd my-hedron-app
    uv add "hedron>=0.20.0,<0.21" "uvicorn[standard]"
    ```

=== "pip (macOS/Linux)"

    ```bash
    mkdir my-hedron-app && cd my-hedron-app
    python -m venv .venv
    source .venv/bin/activate
    python -m pip install "hedron>=0.20.0,<0.21" "uvicorn[standard]"
    ```

=== "pip (Windows PowerShell)"

    ```powershell
    mkdir my-hedron-app; cd my-hedron-app
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install "hedron>=0.20.0,<0.21" "uvicorn[standard]"
    ```

Then create `app.py` from the [quickstart](quickstart.md) (manual / no-scaffold path).

## Supported environments

See the [compatibility policy](../COMPATIBILITY.md) for exact ranges. When evaluating
production use, see [What’s ready today](../guides/whats-ready.md).

## Contributor checkout

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
```

See [Contributing](../CONTRIBUTING.md).
