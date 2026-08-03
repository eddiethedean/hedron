# Installation

The `hedron` package is the recommended starting point for applications. It includes the
framework-neutral rendering core plus FastAPI routing, HTMX responses, security policy,
state, and (on the 0.4 train) command-line tooling.

!!! warning "Which version am I installing?"

    | Source | Version today | What you get |
    |---|---|---|
    | PyPI (`pip install hedron` / `uv add hedron`) | **0.3.0** | Pages, routing, security, HTMX, build basics |
    | Git `main` / pre-release wheel | **0.4.0** | Above + CLI `new`/`check`/`graph`/`audit-components`, plugins, `hedron.testing`, full Explorer |

    These docs describe **0.4.0** behavior. Features marked “requires 0.4 / main” fail on
    PyPI 0.3. See [STATUS](../STATUS.md).

## Create a project (works on PyPI 0.3)

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

Then create `app.py` from the [quickstart](quickstart.md). Do **not** also run
`hedron new` into the same directory unless you are on 0.4 and intend to replace the
scaffold.

## Install 0.4 from `main` (pre-release)

Until `v0.4.0` is tagged on PyPI:

=== "Editable monorepo (contributors)"

    ```bash
    git clone https://github.com/eddiethedean/hedron.git
    cd hedron
    uv sync
    ```

=== "Git dependency in your app"

    ```bash
    uv init my-hedron-app && cd my-hedron-app
    uv add "hedron @ git+https://github.com/eddiethedean/hedron.git#subdirectory=packages/hedron"
    uv add "uvicorn[standard]"
    ```

On 0.4 you can scaffold with the CLI instead of hand-writing files:

```bash
hedron new my-hedron-app
cd my-hedron-app
```

`hedron new` refuses to overwrite a non-empty destination unless you pass `--force`.
The scaffold currently depends on `hedron>=0.4.0`; use a git/`main` install until that
version is on PyPI.

## Choose a package

| Package | Use it when | Install |
|---|---|---|
| `hedron` | You are building a FastAPI web application | `uv add hedron` |
| `hedron-core` | You need framework-neutral component rendering | `uv add hedron-core` |
| `hedron[dev]` | You also want Component Explorer (0.4+) | `uv add "hedron[dev]"` |
| `hedron[browser]` | You need browser and accessibility test helpers (0.4+) | `uv add "hedron[browser]"` |

## Verify the installation

```bash
uv run python -c "import hedron; print(hedron.__version__)"
```

- Prints `0.3.0` → you are on PyPI; use the quickstart pages/routes path; skip 0.4-only CLI and `hedron.testing` until you install from `main`.
- Prints `0.4.0` → full docs apply, including [project workflow](../guides/project-workflow.md) and [testing](../guides/testing.md).

Hedron follows semantic versioning while it moves toward the public API freeze described
in the [roadmap](../ROADMAP.md).

## Supported environments

Hedron supports CPython 3.11–3.14. The flagship integration pins a compatible FastAPI
range; let your package manager resolve it instead of installing FastAPI separately at
an incompatible version. See the [compatibility policy](../COMPATIBILITY.md) for the
full support matrix and deprecation rules.

[Build your first app :material-arrow-right:](quickstart.md){ .md-button .md-button--primary }
