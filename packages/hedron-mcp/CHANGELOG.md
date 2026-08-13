## [Unreleased]

### Fixed

- Default ``resolve_principal`` no longer trusts client-controlled
  ``x-hedron-principal`` / ``x-user`` headers. Identity comes from an
  authenticated session subject or an explicit host ``principal_resolver``
  only (#168).
- Raise the Starlette floor to ``>=1.3.1,<2`` so installs resolve patched
  releases for FormParser, URL authority, StaticFiles, and HTTPEndpoint
  advisories (PYSEC-2026-161 / 248 / 249 / 2280 / 2281).

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
