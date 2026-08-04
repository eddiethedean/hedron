---
status: shipped
---

# CLI reference


!!! note "Stability (0.9 authoring break)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Accepted · **Shipped in 0.4**

Entry point: `hedron` → `hedron.cli:main`.

Global option:

| Flag | Description |
|---|---|
| `--app MODULE:ATTR` | Import path to an application instance or factory used to populate the registry |

Commands are non-interactive by default and do not require Node.js.

## Commands

### `new`

Scaffold an application.

```bash
hedron new my-app
hedron new my-app --path ./apps/my-app --force
```

| Argument / flag | Description |
|---|---|
| `name` | Project name |
| `--path` | Destination directory (default: `./<name>`) |
| `--force` | Allow writing into a non-empty destination |

Exit `0` on success. Refuses to overwrite protected files without `--force`.

### `dev`

Watch CSS, Jinja template extensions, and assets and rebuild atomically.

```bash
hedron dev
hedron dev --project . --interval 0.5
hedron dev --once
```

| Flag | Description |
|---|---|
| `--project` | Project root |
| `--interval` | Poll interval seconds (default `0.5`) |
| `--once` | Build once and exit |

### `build`

Compile CSS and assets into a versioned build manifest. Jinja source is managed by its configured loader.

```bash
hedron build
hedron build --project . --dev
```

| Flag | Description |
|---|---|
| `--project` | Project root |
| `--dev` | Use readable development asset names |

### `check`

Run project diagnostics.

```bash
hedron --app app:app check
hedron check --format json --severity warning
hedron check --format sarif > hedron.sarif
```

| Flag | Description |
|---|---|
| `--project` | Project root |
| `--format` | `text` (default), `json`, or `sarif` |
| `--severity` | Fail when diagnostics meet or exceed `error` (default), `warning`, or `information` |

Exit code is non-zero when diagnostics meet or exceed the severity threshold.
Evergreen information findings do not fail the default `error` gate.

### `routes` / `components` / `graph` / `audit-components`

```bash
hedron --app app:app routes
hedron --app app:app components
hedron --app app:app graph
hedron --app app:app audit-components
```

Emit JSON (or structured text) describing routes, components, dependency edges, and
capability/package audit data. Prefer `--app` whenever importing the app is required to
populate the registry.

### `preview` / `inspect` / `eject`

```bash
hedron --app app:app preview home
hedron --app app:app inspect UserCard
hedron eject UserCard --out ./ejected --force
```

| Command | Purpose |
|---|---|
| `preview <logical_id>` | Inspect a route/component preview payload |
| `inspect <component>` | Explain styles and dependencies |
| `eject <component>` | Write an editable `styles.css` override (`--out`, `--force`) |

## See also

- [Project workflow](../guides/project-workflow.md)
- [Configuration](../CONFIGURATION.md)
- [Diagnostics](../DIAGNOSTICS.md)
