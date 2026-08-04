# Installation

## Prerequisites

- CPython **3.11–3.14**
- A package manager (`pip` or [uv](https://docs.astral.sh/uv/))
- No Node.js required

## Minimum install (FastAPI flagship)

You only need **`hedron`** and a ASGI server for the hello path:

=== "pip"

    ```bash
    pip install "hedron>=0.10.0" "uvicorn[standard]"
    ```

=== "uv"

    ```bash
    uv add hedron "uvicorn[standard]"
    ```

### Recommended: CLI scaffold

=== "pip"

    ```bash
    pip install "hedron>=0.10.0"
    hedron new my-hedron-app
    cd my-hedron-app
    pip install -e .
    uvicorn app:app --reload
    ```

=== "uv"

    ```bash
    # Install the CLI once (tool or venv), then scaffold:
    uv tool install "hedron>=0.10.0"   # or: pip install "hedron>=0.10.0"
    hedron new my-hedron-app
    cd my-hedron-app
    uv sync
    uv run uvicorn app:app --reload
    ```

`hedron new` scaffolds `app.py` and `pyproject.toml`. It refuses to overwrite a non-empty
destination unless you pass `--force`. Do **not** also run `uv init` into the same
directory unless you intend to replace the scaffold.

### Alternative: manual project

=== "uv"

    ```bash
    uv init my-hedron-app
    cd my-hedron-app
    uv add hedron "uvicorn[standard]"
    ```

=== "pip (macOS/Linux)"

    ```bash
    mkdir my-hedron-app && cd my-hedron-app
    python -m venv .venv
    source .venv/bin/activate
    python -m pip install "hedron>=0.10.0" "uvicorn[standard]"
    ```

=== "pip (Windows PowerShell)"

    ```powershell
    mkdir my-hedron-app; cd my-hedron-app
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install "hedron>=0.10.0" "uvicorn[standard]"
    ```

Then create `app.py` from the [quickstart](quickstart.md) (only if you did not use
`hedron new`).

## Verify

=== "pip"

    ```bash
    python -c "import hedron; print(hedron.__version__)"
    ```

=== "uv"

    ```bash
    uv run python -c "import hedron; print(hedron.__version__)"
    ```

Expect **`0.10.0`** (or newer patch) from PyPI. See
[What’s ready today](../guides/whats-ready.md).

[Build your first app :material-arrow-right:](quickstart.md){ .md-button .md-button--primary }

## Optional extras

Install extras only when you need them:

| Extra | When you need it |
|---|---|
| `hedron[data]` | DataTable / DataEditor / data sources |
| `hedron[charts]` | LineChart and visualization adapters |
| `hedron[jinja]` | Optional HDJ (`.hdj`) templates |
| `hedron[dev]` | Component Explorer (`/hedron-explorer/`) |
| `hedron[markdown]` / `[code]` / `[images]` / `[email]` / `[sanitize]` / `[auth]` / `[browser]` | Content, Authlib, or test helpers |

```bash
pip install "hedron[data]"          # example
pip install "hedron[charts]"
pip install "hedron-charts[plotly]" # chart backend after charts extra
```

### Other hosts

| Package | Use when |
|---|---|
| `hedron-flask` | Flask (Supported Beta adapter) |
| `hedron-django` | Django `>=5.2,<6` (Supported Beta adapter) |
| `hedron-core` | Framework-neutral rendering only |

Quickstarts: [Flask](flask.md) · [Django](django.md).

### Component Explorer

With `hedron[dev]` installed and `explorer="development"` on `Hedron(...)`, open
[`/hedron-explorer/`](http://127.0.0.1:8000/hedron-explorer/) while the app is running.
Leave Explorer off in production.

## Supported environments

The flagship integration pins a compatible FastAPI range; let your package manager
resolve it. See the [compatibility policy](../COMPATIBILITY.md).

Maturity vocabulary: [How to read Hedron docs](how-to-read.md).

## Contributor checkout

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
```

See [Contributing](../CONTRIBUTING.md).
