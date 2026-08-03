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

## Environment variables

| Variable | Effect |
|---|---|
| `HEDRON_ENV` | `prod` / `production` selects production mode when `Hedron(production=None)` |
| `HEDRON_BUILD_DIR` | Overrides build directory when not set on the constructor |
| `HEDRON_THEME` | Overrides theme when not forced by constructor overrides |

Secrets (session keys, credentials) belong in your secret manager or process environment,
not in `[tool.hedron]`.

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
changed meaning requires migration documentation and, after `v1.0.0`, the deprecation policy.
