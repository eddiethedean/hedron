# Configuration contract

**Status:** Accepted for the phase 0.0 baseline

Hedron separates build configuration, application construction, deployment configuration, and secrets.

## Sources and precedence

From highest to lowest precedence:

1. Explicit `Hedron(...)`, `HedronRouter(...)`, component, or build-command arguments.
2. Approved `HEDRON_*` environment variables for deployment-level settings.
3. `[tool.hedron]` in the workspace or application `pyproject.toml` for non-secret project/build settings.
4. Security-profile and framework defaults.

Configuration is resolved once at startup or build time into an immutable, redacted settings object. Request data can never alter application configuration.

## Ownership

- `pyproject.toml`: component roots, build output, themes, enabled plugins, asset policy, compiler checks, Explorer development policy, and diagnostic severity overrides.
- Constructor arguments: application-specific routers, lifespan, dependencies, security profile, mounts, and explicit runtime integrations.
- Environment: deployment mode, public origin, proxy/root path, cache/job backend locations, and secret references.
- Application secret manager: credentials, keys, tokens, and other secret values; secrets do not belong in project configuration.

## Security rules

- Production never inherits development Explorer enablement implicitly.
- Strict security policy cannot be weakened by a lower-precedence source.
- Unknown configuration keys fail at startup with suggestions.
- Deprecated keys emit stable diagnostics and migration guidance.
- Resolved configuration shown in Explorer or logs is redacted and annotated with its source, not its secret value.

## Versioning

The `[tool.hedron]` schema and production build manifest include a format version. Unsupported major versions fail clearly. Additive optional keys are backward compatible; changed meaning requires migration documentation and, after `v1.0.0`, the deprecation policy.
