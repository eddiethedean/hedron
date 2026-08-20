---
description: Install the supported Hedron release, optional extras, and Flask or Django adapters.
search:
  boost: 1.7
---

# Installation

Prerequisites, extras, host adapters, and troubleshooting.

The golden-path Hello copy-paste lives on
[Build your first app](quickstart.md) (`hedron new` → Hello → Refresh). Use **this**
page for version pins, optional extras, Flask/Django adapters, and install failures.

Session secrets and `[tool.hedron]` keys: [Configuration](../CONFIGURATION.md).

## Which version to install

This documentation describes the **0.51.x** train. The living in-tree tip is **`v0.51.2`**;
**`v0.51.0` is on PyPI today**. Git tag and PyPI upload for **0.51.2** remain **deferred**
until the cut lands —
use registry-resolvable pins below unless you are developing Hedron itself.

| You are… | Install |
|---|---|
| Building an app from PyPI | `hedron>=0.51.0,<0.52` |
| Working in this repository | `uv sync` (editable **0.51.2**) |

Always use an upper bound so a future minor train cannot install by accident. Packages
are **Beta** (usable, no 1.0, no SLA). Capability detail:
[What’s ready](../guides/whats-ready.md).

## Install from PyPI

### Prerequisites

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
    extras onto that index; pin `hedron>=0.51.0,<0.52`.
    Offline: download wheels on a connected host (`pip download "hedron>=0.51.0,<0.52"`)
    and `pip install --no-index --find-links=...`. TLS / corporate MITM: install your
    org’s CA into the env (`REQUESTS_CA_BUNDLE` / `SSL_CERT_FILE`, or `pip`/`uv`
    trust-store docs). Codespaces still needs a GitHub account and billed minutes — it is
    not an offline playground.

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

Then follow [Build your first app](quickstart.md), or install into an existing project:

=== "uv"

    ```bash
    uv init my-hedron-app
    cd my-hedron-app
    uv add "hedron>=0.51.0,<0.52" "uvicorn[standard]"
    ```

=== "pip (macOS/Linux)"

    ```bash
    mkdir my-hedron-app && cd my-hedron-app
    python -m venv .venv
    source .venv/bin/activate
    python -m pip install "hedron>=0.51.0,<0.52" "uvicorn[standard]"
    ```

=== "pip (Windows PowerShell)"

    ```powershell
    mkdir my-hedron-app; cd my-hedron-app
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install "hedron>=0.51.0,<0.52" "uvicorn[standard]"
    ```

    If PowerShell reports that running scripts is disabled, use
    `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or activate with
    `.\.venv\Scripts\activate.bat` from cmd.exe.

Then create `app.py` from the complete listing on
[Build your first app](quickstart.md) (manual / no-scaffold path). Prefer
`hedron new` when you want the generated project.

### Verify

=== "uv"

    ```bash
    uv run python -c "import hedron; print(hedron.__version__)"
    ```

=== "pip (activated venv)"

    ```bash
    python -c "import hedron; print(hedron.__version__)"
    ```

Expect **`0.51.0`** from PyPI.

If `hedron` is not found after install, prefer **`python -m hedron …`** or see
[Troubleshooting](../guides/troubleshooting.md#hedron-command-not-found).

## This repository (`uv sync`)

Clone only if you are contributing or running in-tree examples:

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
```

This checkout is **0.51.2**. Application installs from PyPI use
`hedron>=0.51.0,<0.52`.

See [Contributing](../CONTRIBUTING.md).

## Optional extras

**You only need `hedron` (+ uvicorn) for Hello and most CRUD/admin apps.** Install
extras only when you need them. Full catalog: [Optional packages](../packages/index.md).

Registry extras use the same PyPI pin as the flagship:

```bash
pip install "hedron[data]>=0.51.0,<0.52"
pip install "hedron[charts]>=0.51.0,<0.52"
pip install "hedron-sample-kit>=0.1.10,<0.2"
```

| Extra | When you need it | Package docs |
|---|---|---|
| `hedron[data]` | DataTable / DataEditor / data sources | [hedron-data](../packages/hedron-data.md) |
| `hedron[dev]` | Component Explorer (`/hedron-explorer/`) | [hedron-explorer](../packages/hedron-explorer.md) |
| `hedron[charts]` | First-party / Matplotlib charts | [hedron-charts](../packages/hedron-charts.md) |
| `hedron[maps]` | First-class maps (`hedron-maps`) | [hedron-maps](../packages/hedron-maps.md) |
| `hedron-flask` / `hedron-django` | Flask or Django host (no FastAPI at runtime) | [Flask](flask.md) · [Django](django.md) |

Other extras (`jinja`, `auth`, `mcp`, `gradio`, `maps`, `elements` **Beta** for Supported
inventory, Workbench/Posit, notebook, native): [Packages](../packages/index.md).

Charts and the sample plugin have explicit compatibility floors. Versions through
`0.1.5` of the sample kit target older cores. Details:
[Compatibility](../COMPATIBILITY.md#charts-and-sample-kit-compatibility-floor) ·
[hedron-charts](../packages/hedron-charts.md) ·
[Charts and HTMX](../guides/charts-and-htmx.md).

!!! note "`hedron[browser]` needs Playwright browsers"

    The `[browser]` extra installs the Playwright **Python** package. You must also
    download browser binaries once per environment:

    ```bash
    pip install "hedron[browser]>=0.51.0,<0.52"
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

## Common install problems

| Symptom | Fix |
|---|---|
| `hedron: command not found` | Use `python -m hedron …`, `uvx --from "hedron>=0.51.0,<0.52" …`, or see [FAQ](../guides/faq.md#hedron-command-not-found) / [Troubleshooting](../guides/troubleshooting.md#hedron-command-not-found) |
| `ModuleNotFoundError: hedron` | Same interpreter as uvicorn; activate the venv, then `pip install -e .` / `uv sync` — [Troubleshooting](../guides/troubleshooting.md#wrong-interpreter-or-modulenotfounderror-for-hedron) |
| FastAPI / pip resolver conflict | Empty venv recommended; see [pin conflicts](../COMPATIBILITY.md#dependency-pin-conflicts) and [Troubleshooting](../guides/troubleshooting.md#fastapi-version-conflict-on-install) |
| `uv add` / “No pyproject.toml” | Create a project first, or use `hedron new` ([FAQ](../guides/faq.md#uv-add-hedron-failed-with-no-pyprojecttoml)) |
| Wrong / old version | Upgrade: `pip install -U "hedron>=0.51.0,<0.52"` — [Troubleshooting](../guides/troubleshooting.md#wrong-or-unexpected-version) |
| CSRF 403 on first POST | Seed cookie with a GET — [Troubleshooting](../guides/troubleshooting.md#csrf-403-on-post-fastapi-flask) |
| Cannot import DataTable | Install `hedron[data]` — [Troubleshooting](../guides/troubleshooting.md#cannot-import-auto-datatable-chart-helpers) |
| Need charts | Install `hedron[charts]>=0.51.0,<0.52` — [Compatibility](../COMPATIBILITY.md#charts-and-sample-kit-compatibility-floor) |
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

## Supported environments

See the [compatibility policy](../COMPATIBILITY.md) for exact ranges. When evaluating
production use, see [What’s ready today](../guides/whats-ready.md).
