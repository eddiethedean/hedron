# RFC-0014: Plugin architecture

**Status:** Proposed

## Purpose

Plugins extend components, renderers, integrations, CLI commands, Explorer panels, HDN helpers, data sources, chart adapters, and build diagnostics without expanding required dependencies.

## Contract

Plugins declare a name, version, Hedron compatibility range, capabilities, optional dependencies, assets, registry contributions, lifecycle hooks, and security implications. Discovery is deterministic and may be disabled. Importing base Hedron does not import plugin dependencies until a contribution is used or startup registration requires it.

Startup occurs in dependency order during application lifespan; shutdown occurs in reverse order. Duplicate identifiers, incompatible versions, dependency cycles, and undeclared browser assets fail at startup with actionable diagnostics.

Installing a plugin is equivalent to installing executable Python code. Hedron reports capabilities and integrates with standard dependency scanners; it does not claim to sandbox plugins.

## Acceptance criteria

- Plugins can be explicitly enabled, disabled, and version-gated.
- Missing optional packages do not prevent unrelated application imports.
- All registered assets and Explorer extensions appear in audits.
- Plugin failures include ownership and dependency context and cannot leave partially registered state.

