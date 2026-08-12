## [0.2.0]

- Production-grade deny-by-default Streamable HTTP MCP projection (phase 0.32 / RFC-0065).
- Host authn reuse, app authz/tenant hooks, bounds, redacted audit, Experimental mutations gated by ``allow_mutations``.
- Pin official ``mcp>=1.9.0,<2`` SDK; Supported inventory only (Beta).


## [0.1.0] — 2026-08-06

### Added

- Initial Alpha release of `McpProjection` (RFC-0043): disabled and empty by
  default, explicit `register_resource` / `register_tool`, principal-bounded
  authz stub, and `mount_mcp` no-op when disabled.
- Optional `hedron.plugins` FeatureManifest registration.
