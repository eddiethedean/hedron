# Installation

Prerequisites, extras, host adapters, and troubleshooting.

The golden-path Hello copy-paste lives on
[Build your first app](quickstart.md) (`hedron new` → Hello → Refresh). Use **this** page
for version checks, optional extras, Flask/Django adapters, and install failures.

Session secrets and `[tool.hedron]` keys: [Configuration](../CONFIGURATION.md).

## Prerequisites

- CPython **3.11–3.14** — verify with `python3 --version` (Windows: `py -3 --version`)
- Use a **clean virtual environment**. Prefer **CI-supported** pins for first apps:
  FastAPI `>=0.141.1,<0.142`, Pydantic `>=2.13.4,<2.14`. Declared install ranges are
  wider (FastAPI `<0.150`, Pydantic `<2.15`) — see [Compatibility](../COMPATIBILITY.md)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended) or `pip`
- No Node.js required

### Installing Python 3.11+

If `python3 --version` is missing or older than 3.11:

| Platform | Suggestion |
|---|---|
| macOS | [python.org](https://www.python.org/downloads/) installer, Homebrew `brew install python@3.12`, or [uv python install 3.12](https://docs.astral.sh/uv/guides/install-python/) |
| Linux | Distro packages (`python3.12`) or `uv python install 3.12` |
| Windows | [python.org](https://www.python.org/downloads/) or `py -3.12`; enable “Add python.exe to PATH” |

After installing, reopen the terminal. Prefer `python3 -m venv .venv` (or `uv venv`) so
system Python is never mixed with the app env. Multiple Pythons: always call the same
interpreter for `pip` / `uv` / `uvicorn` (`which python3`, `py -0p` on Windows).

!!! note "Corporate proxy / air-gapped installs"

    Point `pip` / `uv` at your internal index (`PIP_INDEX_URL`, `UV_INDEX_URL`, or
    `--index-url`). Mirror **PyPI** wheels for `hedron`, `hedron-core`, and matching
    extras onto that index; pin `hedron>=0.38.0,<0.39`. Offline: download wheels on a
    connected host (`pip download "hedron>=0.38.0,<0.39"`) and `pip install --no-index
    --find-links=...`. TLS / corporate MITM: install your org’s CA into the env
    (`REQUESTS_CA_BUNDLE` / `SSL_CERT_FILE`, or `pip`/`uv` trust-store docs). Codespaces
    still needs a GitHub account and billed minutes — it is not an offline playground.

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

Expect **`0.38.0`** or a newer **`0.38.x`** patch on this train. Last published
PyPI/git is **`v0.38.0`**. Pin with `hedron>=0.38.0,<0.39` for
production.

If `hedron` is not found after install, prefer **`python -m hedron …`** or see
[Troubleshooting](../guides/troubleshooting.md#hedron-command-not-found).

## Common install problems

| Symptom | Fix |
|---|---|
| `hedron: command not found` | Use `python -m hedron …`, `uvx --from "hedron>=0.38.0,<0.39" …`, or see [FAQ](../guides/faq.md#hedron-command-not-found) / [Troubleshooting](../guides/troubleshooting.md#hedron-command-not-found) |
| `ModuleNotFoundError: hedron` | Same interpreter as uvicorn; activate the venv, then `pip install -e .` / `uv sync` — [Troubleshooting](../guides/troubleshooting.md#wrong-interpreter-or-modulenotfounderror-for-hedron) |
| FastAPI / pip resolver conflict | Empty venv recommended; see [pin conflicts](../COMPATIBILITY.md#dependency-pin-conflicts) and [Troubleshooting](../guides/troubleshooting.md#fastapi-version-conflict-on-install) |
| `uv add` / “No pyproject.toml” | Create a project first, or use `hedron new` ([FAQ](../guides/faq.md#uv-add-hedron-failed-with-no-pyprojecttoml)) |
| Wrong / old version | `pip install -U "hedron>=0.38.0,<0.39"` — [Troubleshooting](../guides/troubleshooting.md#wrong-or-unexpected-version) |
| CSRF 403 on first POST | Seed cookie with a GET — [Troubleshooting](../guides/troubleshooting.md#csrf-403-on-post-fastapi-flask) |
| Cannot import DataTable | Install `hedron[data]` — [Troubleshooting](../guides/troubleshooting.md#cannot-import-auto-datatable-chart-helpers) |
| Need charts | Install `hedron[charts]>=0.38.0,<0.39` — [Compatibility](../COMPATIBILITY.md#charts-and-sample-kit-compatibility-floor) |
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

**You only need `hedron` (+ uvicorn) for Hello and most CRUD/admin apps.** Install
extras only when you need them:

| Extra | When you need it | Package docs |
|---|---|---|
| `hedron[data]` | DataTable / DataEditor / data sources | [hedron-data](../packages/hedron-data.md) |
| `hedron[jinja]` | Optional HDJ (`.hdj`) templates | [hedron-jinja](../packages/hedron-jinja.md) |
| `hedron[dev]` | Component Explorer (`/hedron-explorer/`) | [hedron-explorer](../packages/hedron-explorer.md) |
| `hedron[conformance]` | Language-neutral conformance kit / CLI runner | [hedron-conformance](../packages/hedron-conformance.md) |
| `hedron[native]` | Optional Rust HTML-escape acceleration (Beta) | [hedron-native](../packages/hedron-native.md) |
| `hedron[extras]` | Curated extras / workbenches | [hedron-extras](../packages/hedron-extras.md) |
| `hedron[notebook]` | Beta tooling-grade localhost notebook preview | [hedron-notebook](../packages/hedron-notebook.md) |
| `hedron[mcp]` | Beta deny-by-default MCP projection (Supported inventory) | [hedron-mcp](../packages/hedron-mcp.md) |
| `hedron[gradio]` | Beta allowlisted Gradio client interoperability | [hedron-gradio](../packages/hedron-gradio.md) |
| `hedron[elements]` | Alpha Web Component ABI incubator | [hedron-elements](../packages/hedron-elements.md) |
| `hedron[otel]` | Optional OpenTelemetry tracing helpers | [Observability](../guides/observability.md) |
| `hedron[markdown]` / `[code]` / `[images]` / `[email]` / `[sanitize]` | Content rendering and validation helpers | [Content API](../api/CONTENT.md) |
| `hedron[auth]` | Authlib-backed OIDC helpers | [OIDC walkthrough](../guides/oidc.md) |
| `hedron[browser]` | Browser testing helpers | [Testing](../guides/testing.md) |

Also install directly (no flagship extra): [hedron-sim](../packages/hedron-sim.md).
Full catalog: [Optional packages](../packages/index.md).

```bash
pip install "hedron[data]>=0.38.0,<0.39"          # example
```

Charts and the sample plugin have explicit compatibility floors:

```bash
pip install "hedron[charts]>=0.38.0,<0.39"
pip install "hedron-sample-kit>=0.1.10,<0.2"
```

Versions through `0.1.5` target older cores. Details:
[Compatibility](../COMPATIBILITY.md#charts-and-sample-kit-compatibility-floor) ·
[hedron-charts](../packages/hedron-charts.md) ·
[Charts and HTMX](../guides/charts-and-htmx.md).

!!! note "`hedron[browser]` needs Playwright browsers"

    The `[browser]` extra installs the Playwright **Python** package. You must also
    download browser binaries once per environment:

    ```bash
    pip install "hedron[browser]>=0.38.0,<0.39"
    playwright install chromium
    ```

    Without `playwright install`, browser tests fail with missing-browser errors. Adopter
    apps do **not** need `[browser]` — it is for testing helpers. Contributors: see
    [Contributing](../CONTRIBUTING.md).

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
    uv add "hedron>=0.38.0,<0.39" "uvicorn[standard]"
    ```

=== "pip (macOS/Linux)"

    ```bash
    mkdir my-hedron-app && cd my-hedron-app
    python -m venv .venv
    source .venv/bin/activate
    python -m pip install "hedron>=0.38.0,<0.39" "uvicorn[standard]"
    ```

=== "pip (Windows PowerShell)"

    ```powershell
    mkdir my-hedron-app; cd my-hedron-app
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install "hedron>=0.38.0,<0.39" "uvicorn[standard]"
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
