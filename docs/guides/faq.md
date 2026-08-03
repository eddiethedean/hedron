# FAQ

## Which version should I install?

```bash
pip install hedron
# or
uv add hedron
```

That installs the current PyPI release on the **0.4** train (`0.4.0` and later patches).
See [STATUS](../STATUS.md).

## Do I need Node.js?

No. Hedron does not require npm or a JavaScript bundler for development or production.

## `uv add hedron` failed with “No pyproject.toml”

Create a project first: `uv init my-app && cd my-app`, then `uv add hedron`. Or use
`hedron new my-app` after `pip install hedron`.

## Should I use `uv init` or `hedron new`?

Either works. Prefer one path: `uv init` + hand-written `app.py` from the quickstart, or
`hedron new` alone. Do not nest both into the same directory by accident.

## Are Auto, DataTable, and charts available?

Not in 0.4. They are **Accepted design contracts** under
[Planned](../api/README.md#planned-contracts) for later phases (starting with 0.5).

## Are the docs “interactive demos” a running Hedron server?

No. They are in-browser simulations. The runnable backend is the
[reference application](https://github.com/eddiethedean/hedron/tree/main/examples/reference-app)
in the repo (`uv sync` after clone).

## Where do I put configuration?

Non-secret project settings go in `[tool.hedron]` (see
[Configuration](../CONFIGURATION.md)). Secrets and deployment mode use environment
variables / your secret store. Constructor args override both when explicit.

## How do I contribute code?

See [Contributing](../CONTRIBUTING.md) for environment setup, tests, and the
specification process.
