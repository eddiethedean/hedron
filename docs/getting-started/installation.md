# Installation

## Prerequisites

- CPython **3.11–3.14**
- A package manager (`pip` or [uv](https://docs.astral.sh/uv/))
- No Node.js required

## Recommended: CLI scaffold

This is the path most new users should follow. Pick **pip** or **uv**, then stop—do not
also hand-write a second `app.py` over the scaffold.

=== "pip"

    ```bash
    pip install "hedron>=0.10.1" "uvicorn[standard]"
    hedron new my-hedron-app
    cd my-hedron-app
    pip install -e .
    uvicorn app:app --reload
    ```

=== "uv"

    ```bash
    uv tool install "hedron>=0.10.1"   # puts `hedron` on your PATH
    hedron new my-hedron-app
    cd my-hedron-app
    uv sync
    uv run uvicorn app:app --reload
    ```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). You should see the scaffold home page.

`hedron new` scaffolds `app.py` and `pyproject.toml`. It refuses to overwrite a non-empty
destination unless you pass `--force`. Do **not** also run `uv init` into the same
directory unless you intend to replace the scaffold.

Then: [Build your first app](quickstart.md) (Path A — after scaffold).

## Verify

=== "pip"

    ```bash
    python -c "import hedron; print(hedron.__version__)"
    ```

=== "uv"

    ```bash
    uv run python -c "import hedron; print(hedron.__version__)"
    ```

Expect **`0.10.1`** (or newer patch) from PyPI.

## Common install problems

| Symptom | Fix |
|---|---|
| `hedron: command not found` | Re-open the shell after install, or use `uv tool install hedron`, or see [FAQ](../guides/faq.md) |
| `uv add` / “No pyproject.toml” | Create a project first, or use `hedron new` ([FAQ](../guides/faq.md#uv-add-hedron-failed-with-no-pyprojecttoml)) |
| Wrong / old version | `pip install -U "hedron>=0.10.1"` — [Troubleshooting](../guides/troubleshooting.md#wrong-or-unexpected-version) |
| CSRF 403 on first POST | Seed cookie with a GET — [Troubleshooting](../guides/troubleshooting.md#csrf-403-on-post-fastapi-flask) |
| Cannot import DataTable / charts | Install extras — [Troubleshooting](../guides/troubleshooting.md#cannot-import-auto-datatable-chart-helpers) |
| Explorer 404 | Install `hedron[dev]` and enable development Explorer — [Troubleshooting](../guides/troubleshooting.md#explorer-404-or-missing-in-production) |
| Production missing manifest | Run `hedron build` before `HEDRON_ENV=production` — [Troubleshooting](../guides/troubleshooting.md#production-startup-missing-manifest-hed-build-0003) |

Full list: [Troubleshooting](../guides/troubleshooting.md) · [FAQ](../guides/faq.md).

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
| `hedron-flask` | Flask |
| `hedron-django` | Django `>=5.2,<6` |
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
    uv add hedron "uvicorn[standard]"
    ```

=== "pip (macOS/Linux)"

    ```bash
    mkdir my-hedron-app && cd my-hedron-app
    python -m venv .venv
    source .venv/bin/activate
    python -m pip install "hedron>=0.10.1" "uvicorn[standard]"
    ```

=== "pip (Windows PowerShell)"

    ```powershell
    mkdir my-hedron-app; cd my-hedron-app
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install "hedron>=0.10.1" "uvicorn[standard]"
    ```

Then create `app.py` from the [quickstart](quickstart.md) (Path B).

## Supported environments

The flagship integration pins a compatible FastAPI range; let your package manager
resolve it. See the [compatibility policy](../COMPATIBILITY.md).

When evaluating production use, see [What’s ready today](../guides/whats-ready.md) and
[Evaluate Hedron](../guides/evaluate.md). Maturity vocabulary:
[How to read Hedron docs](how-to-read.md).

## Contributor checkout

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
```

See [Contributing](../CONTRIBUTING.md).
