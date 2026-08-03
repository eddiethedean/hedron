# Installation

The `hedron` package is the recommended starting point for applications. It includes the
framework-neutral rendering core plus FastAPI routing, HTMX responses, security policy,
state, and command-line tooling.

## Create a project

=== "uv"

    ```bash
    uv init my-hedron-app
    cd my-hedron-app
    uv add hedron uvicorn
    ```

=== "pip"

    ```bash
    mkdir my-hedron-app && cd my-hedron-app
    python -m venv .venv
    source .venv/bin/activate
    python -m pip install hedron uvicorn
    ```

!!! tip "Let the CLI scaffold the files"

    After installing Hedron, `hedron new my-hedron-app` creates `app.py`,
    `pyproject.toml`, and a component directory. The command refuses to overwrite a
    non-empty destination unless you explicitly pass `--force`.

## Choose a package

| Package | Use it when | Install |
|---|---|---|
| `hedron` | You are building a FastAPI web application | `uv add hedron` |
| `hedron-core` | You need framework-neutral component rendering | `uv add hedron-core` |
| `hedron[dev]` | You also want Component Explorer | `uv add "hedron[dev]"` |
| `hedron[browser]` | You need browser and accessibility test helpers | `uv add "hedron[browser]"` |

## Verify the installation

```bash
uv run python -c "import hedron; print(hedron.__version__)"
```

The installed version should print without an import error. Hedron follows semantic
versioning while it moves toward the public API freeze described in the
[roadmap](../ROADMAP.md).

## Supported environments

Hedron supports CPython 3.11–3.14. The flagship integration pins a compatible FastAPI
range; let your package manager resolve it instead of installing FastAPI separately at
an incompatible version. See the [compatibility policy](../COMPATIBILITY.md) for the
full support matrix and deprecation rules.

[Build your first app :material-arrow-right:](quickstart.md){ .md-button .md-button--primary }
