## [Unreleased]

### Fixed

- Default ``resolve_principal`` no longer trusts client-controlled
  ``x-hedron-principal`` / ``x-user`` headers. Identity comes from an
  authenticated session subject or an explicit host ``principal_resolver``
  only (#168).
- Raise the Starlette floor to ``>=1.3.1,<2`` so installs resolve patched
  releases for FormParser, URL authority, StaticFiles, and HTTPEndpoint
  advisories (PYSEC-2026-161 / 248 / 249 / 2280 / 2281).
- Streamable HTTP ``DELETE /mcp`` terminates the session identified by
  ``mcp-session-id``; initialize mints and returns server session ids and
  subsequent requests reject principal mismatches on an existing session (#173).
- Cap and TTL-evict process-local cancel ids, sessions, and rate-bucket keys so
  long-lived MCP workers cannot retain unbounded memory (#172).
- ``notifications/cancelled`` marks the client JSON-RPC ``requestId`` so matching
  ``tools/call`` / ``resources/read`` requests fail closed; cancel no longer
  tears down the MCP session. Async tool handlers remain unsupported (#171).

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
