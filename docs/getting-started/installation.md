# Installation

The `hedron` package is the recommended starting point for applications. It includes the
framework-neutral rendering core plus FastAPI routing, HTMX responses, security policy,
state, CLI tooling, plugins, and testing helpers.

## Create a project

=== "uv"

    ```bash
    uv init my-hedron-app
    cd my-hedron-app
    uv add hedron "uvicorn[standard]"
    ```

=== "pip"

    ```bash
    mkdir my-hedron-app && cd my-hedron-app
    python -m venv .venv
    source .venv/bin/activate
    python -m pip install hedron "uvicorn[standard]"
    ```

=== "CLI scaffold"

    ```bash
    pip install hedron
    hedron new my-hedron-app
    cd my-hedron-app
    ```

`hedron new` creates `app.py`, `pyproject.toml`, and a component directory. It refuses to
overwrite a non-empty destination unless you pass `--force`. Do not run `uv init` and
`hedron new` into the same directory unless you intend to replace the scaffold.

Then follow the [quickstart](quickstart.md), or use the generated `app.py` from
`hedron new`.

## Choose a package

| Package | Use it when | Install |
|---|---|---|
| `hedron` | You are building a FastAPI web application | `uv add hedron` |
| `hedron-core` | You need framework-neutral component rendering | `uv add hedron-core` |
| `hedron[data]` | You need DataTable / DataEditor / data sources | `uv add "hedron[data]"` |
| `hedron[dev]` | You also want Component Explorer | `uv add "hedron[dev]"` |
| `hedron[browser]` | You need browser and accessibility test helpers | `uv add "hedron[browser]"` |

## Verify the installation

```bash
uv run python -c "import hedron; print(hedron.__version__)"
```

The installed version should print `0.5.0` (or a later patch on the 0.5 train) without an
import error. Data APIs require `hedron-data` (`pip install "hedron[data]"`). Hedron follows
semantic versioning while it moves toward the public API freeze described in the
[roadmap](../ROADMAP.md).

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

[Build your first app :material-arrow-right:](quickstart.md){ .md-button .md-button--primary }
