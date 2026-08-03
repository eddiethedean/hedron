# FAQ

## Why does `pip install hedron` give me 0.3.0 while the docs say 0.4?

These docs describe package version **0.4.0** on `main`, which is ready to cut.
**PyPI still serves 0.3.0** until the `v0.4.0` tag publishes. See
[STATUS](../STATUS.md) and the [installation matrix](../getting-started/installation.md).

## Why is `hedron new` / `hedron check` / `hedron.testing` missing?

Those ship in **0.4**. On PyPI 0.3 they are absent. Install from `main` or wait for the
release tag.

## Do I need Node.js?

No. Hedron does not require npm or a JavaScript bundler for development or production.

## `uv add hedron` failed with “No pyproject.toml”

Create a project first: `uv init my-app && cd my-app`, then `uv add hedron`.

## Should I use `uv init` or `hedron new`?

On PyPI 0.3, use `uv init` (or pip + venv) and write `app.py` from the quickstart.
On 0.4 / main, either works—do not nest both into the same directory by accident.

## Are Auto, DataTable, and charts available?

Not in 0.4. They are **Accepted design contracts** under
[Planned](../api/README.md#planned-contracts) for later phases.

## Are the docs “live examples” a running Hedron server?

No. They are in-browser simulations. The runnable backend is the
[reference application](https://github.com/eddiethedean/hedron/tree/main/examples/reference-app)
in the repo.

## Where do I put configuration?

Non-secret project settings go in `[tool.hedron]` (see
[Configuration](../CONFIGURATION.md)). Secrets and deployment mode use environment
variables / your secret store. Constructor args override both when explicit.

## How do I contribute code?

See [Contributing](../CONTRIBUTING.md) for environment setup, tests, and the
specification process.
