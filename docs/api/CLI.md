---
status: shipped
---

# CLI reference


!!! note "Stability (0.9 authoring break)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Stable 1.0 command surface; advanced commands retain their documented levels

Entry points: console script `hedron` → `hedron.cli:main`, and
**`python -m hedron`** (same CLI; PATH-independent).

`hedron new` writes `app.py`, `pyproject.toml`, and an empty `components/` directory.

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
mkdir my-app && cd my-app
python3.11 -m venv .venv
source .venv/bin/activate
python3.11 -m pip install "hedron>=0.66.2,<0.67"
hedron new my-app --path . --force
hedron new my-flask-app --flask
hedron new my-django-app --django
```

| Argument / flag | Description |
|---|---|
| `name` | Project name |
| `--path` | Destination directory (default: `./<name>`) |
| `--force` | Allow writing into a non-empty destination; a directory containing only `.venv` is already accepted |
| `--flask` | Scaffold a Flask + `hedron-flask` app without FastAPI |
| `--django` | Scaffold a Django + `hedron-django` app without FastAPI |
| `--template` | FastAPI template: `minimal` (default), `crud`, `dashboard`, or `task` |

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
| `--all-compat` | Include global adapter/extra compatibility notices even when those integrations are not detected |

Exit code is non-zero when diagnostics meet or exceed the severity threshold.
Evergreen information findings do not fail the default `error` gate.
Adapter-specific notices such as the Django floor (`HED-COMPAT-0002`) and experimental
Plotly/Altair status (`HED-COMPAT-0003`) appear only when the project references those
surfaces (or when `--all-compat` is set). The generic baseline notice (`HED-COMPAT-0001`)
always remains available.

### `security-check`

Offline security posture report for the project tree. Read-only: does not probe
production hosts or open network connections.

```bash
hedron security-check
hedron security-check --format json
hedron security-check --format sarif --policy strict --strict
```

| Flag | Description |
|---|---|
| `--project` | Project root (default: `.`) |
| `--format` | `text` (default), `json`, or `sarif` |
| `--policy` | `SecurityPolicy` preset: `development`, `standard` (default), or `strict` |
| `--suppressions` | JSON suppressions file (expiring entries) |
| `--baseline` | Reviewed baseline fingerprints JSON for drift detection |
| `--strict` | Fail on proven warnings and baseline drift |

Exit code is non-zero for proven errors, and in `--strict` mode also for proven warnings
and baseline drift. Findings include evidence, ownership, and remediation; secrets are
redacted in all formats.

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

### `testgen`

Generate reviewable interaction pytest stubs from a sealed interaction catalog
(TESTGEN-053). Never evaluates catalog fields — only embeds redacted literals.

```bash
hedron --app app:app testgen
hedron --app app:app testgen --profile ci --out tests/generated/test_interactions.py
```

| Flag | Description |
|---|---|
| `--profile` | Generator profile label embedded in the source (default `default`) |
| `--generator-version` | Override embedded generator version |
| `--out` | Write source to a file instead of stdout |

### `discover`

Print the curated public-API stability inventory (DISCOVER-053).

```bash
hedron discover
hedron discover --format human
```

| Flag | Description |
|---|---|
| `--format` | `json` (default) or `human` |

### `fleet`

Diagnose the installed package fleet: extras, train skew, assets/plugins, and
capability recommendations (FLEET-053).

```bash
hedron fleet
hedron fleet --format json
```

| Flag | Description |
|---|---|
| `--format` | `json` (default) or `human` |

### `package doctor`

Run read-only validation of an external Hedron plugin package source tree
(DOCTOR-054). This checks package metadata, entry points, bundled assets, typing
markers, compatibility declarations, and the package's conformance fixtures.

```bash
hedron package doctor ./my-plugin
hedron package doctor ./my-plugin --format json
```

| Argument / flag | Description |
|---|---|
| `path` | Package source tree to inspect (default: current directory) |
| `--format` | `human` (default) or `json` |

The command exits `0` when every package-author check passes and `1` when the
report contains failures. Unlike `hedron fleet`, it inspects a source tree rather
than the currently installed package fleet.

### `upgrade-report`

Offline application upgrade compatibility report (UPGRADE-055). Never contacts
external services. Emits CI-consumable JSON distinguishing definite breaks from
heuristic warnings.

```bash
hedron upgrade-report --from 0.56.0 --to 0.55.0
hedron upgrade-report --from 0.56.0 --to 0.55.0 --manifest ./manifest.json --out report.json
```

| Flag | Description |
|---|---|
| `--from` | Current train tip |
| `--to` | Target train tip |
| `--baseline` | Reviewed baseline JSON (fail closed on schema mismatch) |
| `--manifest` | Optional `WorkflowManifest` JSON for heuristic findings |
| `--out` | Write JSON to a file instead of stdout |
| `--allow-definite` | Exit `0` even when definite breaks are present |

Exit `0` when clean or heuristic-only (unless `--allow-definite` is unset and
definite findings exist — then exit `2`). Exit `1` on malformed input.

### `preview` / `inspect` / `explain` / `eject`

```bash
hedron --app app:app preview home
hedron --app app:app inspect UserCard
hedron --app app:app explain features:notes --format json
hedron eject UserCard --out ./ejected --force
hedron --app app:app eject features:notes --surface list_view --out ./ejected --overwrite
```

| Command | Purpose |
|---|---|
| `preview <logical_id>` | Inspect a route/component preview payload |
| `inspect <component>` | Explain styles and dependencies. With `hedron-explorer` installed, identities match Explorer HTML/JSON (HEADLESS-050); otherwise the skip is labeled. |
| `inspect interactions` | Read-only interaction catalog |
| `inspect htmx-extensions` | Declared HTMX extension catalog |
| `inspect features` | Included FeatureBundles |
| `explain features:<id>` | Static redacted feature explanation (`--format human|json`) |
| `explain design` / `style explain` / `style preview` / `style diff` | Static redacted DesignSystem plan, styling explanation, gallery preview, and design diff (0.60) |
| `eject <component>` | Write `accessibility_contract.json` plus an editable `styles.css` override (`--out`, `--force`) |
| `eject features:<id>` | Write reviewable explicit-registration Python for a bundle (`--surface`, `--out`, `--overwrite`) |

### `conformance`

Run the published language-neutral fixture kit. Install `hedron[conformance]` first.

```bash
hedron conformance
hedron conformance --json
```

Without `hedron-conformance`, the command explains the required extra and exits `2`.
Fixture failures return the conformance runner’s non-zero status.

### `theme check` / `style check` / `style preview`

Validate a design system without running the application.

```bash
hedron theme check
hedron theme check --theme aurora --format json
hedron style check --zero-app-css examples/chrome-zero-css
hedron --app app:app style preview --mode all
hedron --app app:app style diff --base default --candidate acme
```

`theme check` reports missing accessibility tokens, element token/style-contract
gaps, and contrast findings: text pairs (`color.fg`/`color.bg`,
`color.muted`/`color.bg`, `color.on-accent`/`color.accent`,
`color.on-danger`/`color.danger`) must clear 4.5:1 and `color.accent` on
`color.bg` must clear 3:1. Non-literal token values such as `var(...)` are
skipped because they cannot be measured statically.

`style explain`, `style preview`, and `style diff` are static redacted styling tooling (0.60); they
do not execute application callbacks or emit secrets.

`style check --zero-app-css PATH` fails when the path contains an
application-authored stylesheet (`.css`, `.scss`, `.sass`, `.less`, `.styl`) or a
`<style>` block or `style=` attribute in markup, reported as `HED-CSS-0009`.

### `accel-status`

Report whether optional `hedron-native` acceleration is loaded, disabled, absent, or using
the pure-Python fallback.

```bash
hedron accel-status
```

An absent or disabled native extension is a valid configuration and exits `0`; correctness
always falls back to the reference Python serializer.

### `run`

Run an ASGI application with Uvicorn. When Posit Workbench is explicitly selected or
`RS_SERVER_URL` is present, delegate pre-import mount discovery to `hedron-posit` when
the `hedron[posit]` extra is installed.

```bash
hedron run app:app --reload
hedron run app:create_app --factory
hedron run app:app --workbench --workbench-mode on
```

| Flag | Description |
|---|---|
| `--host`, `--port` | Bind address and port (local defaults: `127.0.0.1:8000`) |
| `--reload` | Enable Uvicorn reload |
| `--workers` | Worker count (default `1`) |
| `--factory` | Treat the target as an application factory |
| `--debug` | Use debug logging |
| `--workbench` | Force the Workbench launcher path |
| `--workbench-mode` | `auto`, `on`, or `off` |
| `--mount`, `--public-base-url` | Explicit proxy/mount settings |
| `--forwarded-allow-ips` | Trusted proxy allowlist |
| `--allow-external-bind` | Permit a reviewed non-loopback bind |
| `--topology` | `auto`, `local`, `launcher-local`, `launcher-kubernetes`, `launcher-slurm`, or `reverse-proxy` |

The target must be `module:attribute` (or supplied through global `--app`). A detected
Workbench runtime without `hedron[posit]` exits `2` with an install hint.

### `migrate api`

Audit and mechanically migrate transitional 0.67 API paths for the 1.0 surface. The command is
static and never imports or executes the inspected project. By default it prints a report; use
`--diff` to show proven replacements, `--out` to write a fresh output file/tree, or `--apply` for
an explicit in-place update. Existing output is never overwritten.

```bash
hedron migrate api --target 1.0 .
hedron migrate api --target 1.0 . --diff --format json
hedron migrate api --target 1.0 app.py --out migrated-app.py
```

`app.component` and `app.include_feature` are mechanically renamed. Region-specific
`app.fragment` calls are reported with `partial` confidence and remain unchanged for review.
Text/template occurrences are also reported, but are never automatically rewritten.

### `migrate streamlit`

Statically analyze a Streamlit entrypoint or project and optionally generate a reviewable
Hedron scaffold. The assistant parses source; it does not execute the Streamlit application.

```bash
hedron migrate streamlit streamlit_app.py --analyze-only
hedron migrate streamlit streamlit_app.py --analyze-only --format sarif
hedron migrate streamlit streamlit_app.py --out ./migrated-app --python-version 3.12
```

| Flag | Description |
|---|---|
| `--out` | Fresh output directory; required unless `--analyze-only` |
| `--project-root` | Boundary for local-module discovery |
| `--analyze-only` | Report without generating files |
| `--format` | `text`, `json`, or `sarif` |
| `--python-version` | Parser grammar: Python 3.10–3.14 |
| `--fail-on` | Return `2` when findings reach `information`, `warning`, or `error` (default) |

Exit `1` covers invalid input or generation failure; exit `2` means review findings met the
configured threshold. See the [Streamlit migration guide](../guides/streamlit-migration.md).

## Errors / exit codes

| Situation | Behavior |
|---|---|
| Success | Exit `0` |
| Diagnostics at/above `--severity` on `check` | Non-zero exit |
| `new` into non-empty dir without `--force` | Refuse; non-zero |
| Missing `--app` when registry import required | Import/empty-registry failure or incomplete output |
| Missing optional package for a command | Install hint and non-zero exit where required (for example, conformance or Workbench runtime) |
| Unknown command / bad args | argparse error; non-zero |

## See also

- [Project workflow](../guides/project-workflow.md)
- [Configuration](../CONFIGURATION.md)
- [Diagnostics](https://github.com/eddiethedean/hedron/blob/main/docs/DIAGNOSTICS.md)
