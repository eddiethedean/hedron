# Installation

The recommended path for new applications is **`hedron new`**, which scaffolds `app.py`,
`pyproject.toml`, and a component directory for the current train. Install Hedron first
so the `hedron` CLI is on your `PATH`.

## Recommended: CLI scaffold

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

`hedron new` depends on `hedron>=0.10.0` and `uvicorn[standard]`. It refuses to overwrite a
non-empty destination unless you pass `--force`. Do **not** also run `uv init` into the same
directory unless you intend to replace the scaffold.

## Alternative: manual project

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

Then create `app.py` from the [quickstart](quickstart.md).

### Component Explorer

With `hedron[dev]` installed and `explorer="development"` on `Hedron(...)`, open
[`/hedron-explorer/`](http://127.0.0.1:8000/hedron-explorer/) while the app is running.
Leave Explorer off in production.

## Choose a package

| Package | Use it when | pip | uv |
|---|---|---|---|
| `hedron` | You are building a FastAPI web application | `pip install "hedron>=0.10.0"` | `uv add hedron` |
| `hedron-flask` | You need Flask (Supported Beta adapter) | `pip install hedron-flask` | `uv add hedron-flask` |
| `hedron-django` | You need Django `>=5.2,<6` (Supported Beta adapter) | `pip install hedron-django` | `uv add hedron-django` |
| `hedron-core` | You need framework-neutral component rendering | `pip install hedron-core` | `uv add hedron-core` |
| `hedron[jinja]` / `hedron-jinja` | You need optional HDJ (`.hdj`) templates over Jinja/HTML/HTMX | `pip install "hedron[jinja]"` | `uv add "hedron[jinja]"` |
| `hedron[data]` | You need DataTable / DataEditor / data sources | `pip install "hedron[data]"` | `uv add "hedron[data]"` |
| `hedron[charts]` | You need LineChart and visualization adapters | `pip install "hedron[charts]"` | `uv add "hedron[charts]"` |
| `hedron[markdown]` | You need Markdown rendering | `pip install "hedron[markdown]"` | `uv add "hedron[markdown]"` |
| `hedron[code]` | You need Pygments code highlighting | `pip install "hedron[code]"` | `uv add "hedron[code]"` |
| `hedron[images]` | You need Pillow image helpers | `pip install "hedron[images]"` | `uv add "hedron[images]"` |
| `hedron[email]` | You need email address validation helpers | `pip install "hedron[email]"` | `uv add "hedron[email]"` |
| `hedron[sanitize]` | You need nh3 HTML sanitization (`TrustedHtml.nh3`) | `pip install "hedron[sanitize]"` | `uv add "hedron[sanitize]"` |
| `hedron[auth]` | You need Authlib helpers | `pip install "hedron[auth]"` | `uv add "hedron[auth]"` |
| `hedron[dev]` | You also want Component Explorer (`/hedron-explorer/`) | `pip install "hedron[dev]"` | `uv add "hedron[dev]"` |
| `hedron[browser]` | You need browser and accessibility test helpers | `pip install "hedron[browser]"` | `uv add "hedron[browser]"` |

Chart backends are optional on top of `hedron-charts`:

| Extra | Backend |
|---|---|
| `hedron-charts[matplotlib]` | Matplotlib static charts |
| `hedron-charts[plotly]` | Plotly interactive charts |
| `hedron-charts[altair]` | Altair / Vega-Lite charts |

Or install a backend through the flagship package once `hedron[charts]` is present
(for example `pip install "hedron-charts[plotly]"`).

## Verify the installation

=== "pip"

    ```bash
    python -c "import hedron; print(hedron.__version__)"
    ```

=== "uv"

    ```bash
    uv run python -c "import hedron; print(hedron.__version__)"
    ```

The installed version should print without an import error. Expect **`0.10.0`** from PyPI for the
current live-interaction train—see [What’s ready today](../guides/whats-ready.md). Data APIs require
`hedron-data` (`pip install "hedron[data]"`). Charts require `hedron-charts`
(`pip install "hedron[charts]"`). Hedron follows semantic versioning; see the
[public roadmap](../guides/roadmap.md) and [compatibility policy](../COMPATIBILITY.md).

## Prerequisites

- CPython **3.11–3.14**
- A package manager (`pip` or [uv](https://docs.astral.sh/uv/))
- No Node.js required

## Contributor checkout

To work on Hedron itself:

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
```

See [Contributing](../CONTRIBUTING.md).

## Supported environments

Hedron supports CPython 3.11–3.14. The flagship integration pins a compatible FastAPI
range; let your package manager resolve it instead of installing FastAPI separately at
an incompatible version. See the [compatibility policy](../COMPATIBILITY.md) for the
full support matrix and deprecation rules.

New to the maturity vocabulary? Read [How to read Hedron docs](how-to-read.md).

[Build your first app :material-arrow-right:](quickstart.md){ .md-button .md-button--primary }
