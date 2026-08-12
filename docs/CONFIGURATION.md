# Configuration reference

**Status:** Accepted · **Shipped schema in 0.4**

Hedron separates build configuration, application construction, deployment configuration,
and secrets. Unknown `[tool.hedron]` keys fail at load time with suggestions.

## Sources and precedence

From highest to lowest precedence:

1. Explicit `Hedron(...)`, `HedronRouter(...)`, component, or build-command arguments.
2. Approved `HEDRON_*` environment variables for deployment-level settings.
3. `[tool.hedron]` in `pyproject.toml` for non-secret project/build settings.
4. Security-profile and framework defaults.

Configuration is resolved at startup or build time. Request data cannot alter application
configuration.

## `[tool.hedron]` keys

| Key | Type | Default | Description |
|---|---|---|---|
| `format_version` | `int` | `1` | Schema version; unsupported values fail |
| `component_roots` | `list[str]` | `[]` | Relative dirs searched for component folders |
| `build_dir` | `str` | `".hedron/build"` | Build/manifest output directory |
| `theme` | `str` \| omit | `"default"` | Registered theme name |
| `plugins` | `list[str]` \| omit | unset (`null`) | `null`/omit = discover all entry points; `[]` = load none; names = exact enable list |
| `explorer` | `str` | `"off"` | `"off"` \| `"development"` \| `"secured"` (constructor may override) |
| `compiler_checks` | `bool` | `true` | Enable compiler diagnostics in check/build |
| `diagnostic_severities` | `table[str, str]` | `{}` | Override severity by diagnostic code |
| `asset_policy` | table | see below | Asset/CSP related build policy |

### `[tool.hedron.asset_policy]`

| Key | Type | Default | Description |
|---|---|---|---|
| `allow_remote` | `bool` | `false` | Allow remote asset URLs |
| `strict_csp` | `bool` | `true` | Prefer strict stylesheet CSP |
| `registered_roots` | `list[str]` | `[]` | Extra registered asset roots |
| `reject_inline_style` | `bool` | `true` | Reject inline style authoring where gated |

### Example

```toml
[tool.hedron]
format_version = 1
component_roots = ["components"]
build_dir = ".hedron/build"
theme = "default"
plugins = []
explorer = "off"

[tool.hedron.asset_policy]
allow_remote = false
strict_csp = true
reject_inline_style = true
```

## HDJ runtime configuration

Format v1 is configured directly on `HedronJinja(...)`. Hedron does not consume a
`[tool.hedron.jinja]` table for these runtime knobs, so project-file keys cannot appear to
work while being ignored.

| Key | Type | Default | Description |
|---|---|---:|---|
| `strict` | `bool` | `true` | Require strict undefined, autoescape, static contracts, and contextual checks for dynamic data; literal trusted source remains standards-complete |
| `allowed_capabilities` | `Iterable[str]` | `()` | Exact format-v1 browser/network capability allowlist; declarations remain separate assertions |
| `max_dependency_depth` | `int` | `32` | Maximum static include/extends/import nesting |
| `max_component_invocations` | `int` | `10_000` | Maximum Hedron tags in one render |
| `max_output_chars` | `int` | `10_000_000` | Maximum emitted Unicode characters |
| `max_metadata_items` | `int` | `10_000` | Maximum accumulated metadata entries |
| `url_builder` / `csrf_builder` | callback or `None` | `None` | Optional application-owned portable URL and CSRF bridges |

HTMX selector/attribute options, application roots, SecurityPolicy/CSP reconciliation,
async/macro/loop budgets, and richer analyzer options are documented with the HDJ /
Jinja surfaces — see [HDJ API](api/JINJA.md) and [COMPATIBILITY](COMPATIBILITY.md).

Runtime arguments may tighten these limits. A production override may not silently weaken build
policy. Format-v1 inline/eval/remote browser capabilities are checked against
`allowed_capabilities`. Jinja loaders, bytecode caches,
extensions, filters, tests, globals, and i18n remain Python environment configuration, not
serialized project objects.

The mandatory `.hdj` prologue is source-owned and is not replaced by project defaults. Configuration
may deny a declared feature or capability, but cannot silently add one to source. The format version,
profile expansion, feature IDs, and prologue schema are defined by RFC-0031.

## Environment variables

| Variable | Effect |
|---|---|
| `HEDRON_ENV` | `prod` / `production` selects production mode when `Hedron(production=None)` |
| `HEDRON_BUILD_DIR` | Overrides build directory when not set on the constructor |
| `HEDRON_THEME` | Overrides theme when not forced by constructor overrides |
| `HEDRON_REDIS_URL` | Optional. Used by sample/compose job backends that speak Redis; omit for ordinary page apps |
| `HEDRON_ROOT_PATH` | Construction-time mount for session/CSRF cookie `Path` and asset prefixes. Required under a reverse-proxy subpath; uvicorn `--root-path` alone does not scope cookies |
| `HEDRON_TRUSTED_PROXIES` | Optional comma-separated peer allowlist for `X-Forwarded-Proto` (CSRF Secure) and related trusted-header checks |
| `HEDRON_WORKBENCH_MODE` | `auto` / `on` / `off` for `hedron-workbench` (optional extra) |
| `HEDRON_WORKBENCH_MOUNT` | Explicit browser mount; exported to `HEDRON_ROOT_PATH` before app import |
| `HEDRON_WORKBENCH_HOST` / `HEDRON_WORKBENCH_PORT` | Loopback bind (default `127.0.0.1`, port `0`) |
| `HEDRON_WORKBENCH_PUBLIC_BASE_URL` | Optional public origin; must not conflict with mount |
| `HEDRON_WORKBENCH_RSERVER_URL` | Absolute path to `rserver-url` (default `/usr/lib/rstudio-server/bin/rserver-url`) |
| `HEDRON_WORKBENCH_DEBUG` | Redacted scope logs from path middleware |
| `HEDRON_WORKBENCH_FORWARDED_ALLOW_IPS` | Exact comma-separated proxy IP allowlist shared by Uvicorn and Hedron; wildcard trust is rejected |
| `HEDRON_WORKBENCH_ALLOW_EXTERNAL_BIND` | Explicit opt-in for a non-loopback listener; default is false |
| `HEDRON_WORKBENCH_WORKERS` / `HEDRON_WORKBENCH_RELOAD` | Parsed for diagnostics; the pre-bound runner rejects values other than one worker / no reload |
| `RS_SERVER_URL` | Discovery trigger only — never wraps or grants trust |
| `WORKBENCH_FORCE` / `BASE_PATH` / `PUBLIC_BASE_URL` / `HOST` / `PORT` | Launcher compatibility aliases; warn (`HED-WB-0008`); namespaced vars win. Inactive `HedronWorkbench` ignores broad aliases to preserve ordinary-host behavior |

### Session secrets (application-owned)

`Hedron` takes `session_secret=` on the constructor. There is **no** built-in env var that
sets it automatically. Adopter convention for Docker/K8s:

| Variable | Effect |
|---|---|
| `HEDRON_SESSION_SECRET` | **Your** `app.py` should pass `session_secret=os.environ["HEDRON_SESSION_SECRET"]` (or your secret manager’s equivalent). Hedron does not read this name itself. |

Adapter hosts also require framework secrets outside this table (Flask `SECRET_KEY`,
Django `SECRET_KEY`).

Secrets (session keys, credentials) belong in your secret manager or process environment,
not in `[tool.hedron]`. See [Deployment](guides/deployment.md).

## Ownership

- `pyproject.toml`: component roots, build output, themes, plugins, asset policy, compiler checks, Explorer policy, diagnostic severity overrides.
- Constructor arguments: routers, lifespan, dependencies, security profile, mounts, runtime integrations.
- Environment: deployment mode, build dir/theme overlays, secret references.
- Application secret manager: credentials, keys, tokens.

## Security rules

- Production never inherits development Explorer enablement implicitly (`development` is forced off).
- Strict security policy cannot be weakened by a lower-precedence source.
- Unknown configuration keys fail at startup with suggestions.
- Resolved configuration shown in Explorer or logs is redacted.

## Versioning

The `[tool.hedron]` schema and production build manifest include a format version.
Unsupported major versions fail clearly. Additive optional keys are backward compatible;
changed meaning requires migration documentation and the compatibility/deprecation policy.
