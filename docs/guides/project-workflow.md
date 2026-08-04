# Project workflow

Hedron's CLI is non-interactive by default and emits stable, automation-friendly output.
Use it to keep local development and CI on the same compilation path.

## Scaffold

```bash
hedron new my-app
cd my-app
```

The scaffold includes an application, project metadata, and a component root. Existing
files are protected unless you explicitly use `--force`.

## Develop

```bash
hedron dev
```

The development command watches Python, scoped CSS, and existing experimental HDN (`.hdn`),
and registered assets, then rebuilds affected artifacts without exposing a partially compiled
registry.

If you prefer your existing ASGI workflow, run `uvicorn app:app --reload`; Hedron remains
a normal FastAPI application.

## Inspect

```bash
hedron --app app:app routes
hedron --app app:app components
hedron --app app:app inspect UserCard
hedron --app app:app graph
```

These commands expose the registry Hedron will use: route methods and operation IDs,
component identity and assets, resolved templates and styles, and dependency edges.
Pass `--app module:attribute` whenever importing the application is required to populate
the registry.

## Check in CI

```bash
hedron --app app:app check --format text
hedron --app app:app check --format sarif > hedron.sarif
hedron --app app:app audit-components
```

Diagnostics carry stable `HED-*` codes and actionable remediation. SARIF output can be
uploaded to code scanning systems; JSON is available when another tool owns presentation.

## Build for production

```bash
hedron build
```

The production build compiles CSS and existing experimental HDN compatibility sources, fingerprints assets, records the selected
theme and settings digest, and writes a manifest consumed by the application. The runtime
checks this sealed boundary instead of compiling mutable sources on demand.

!!! note

    Exact flags and configuration keys are versioned public contracts. See the
    [CLI reference](../api/CLI.md) and [configuration reference](../CONFIGURATION.md)
    when integrating commands into deployment automation.
