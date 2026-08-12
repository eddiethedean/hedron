# Alpha `0.1.x` → Beta `0.2.0` upgrade fixtures (PROTOCOL-032 / PKG-032)

Baseline: Published Hedron tip `v0.31.0` with Experimental Alpha `hedron-mcp`
`0.1.x` (RFC-0043 / `MCP-017`).

## Public API continuity

These symbols remain importable across the upgrade (RFC-0043 product contract):

- `AuthorizationError`
- `McpProjection`
- `McpResource`
- `McpTool`
- `mount_mcp`
- `__version__`

## Behavioral deltas at `0.2.0`

| Topic | Alpha `0.1.x` | Beta `0.2.0` Supported |
|---|---|---|
| Transport | Marker-only `app.state.hedron_mcp` | Streamable HTTP JSON-RPC mount |
| Authz | Principal stub | Host authn reuse + app authz/tenant hooks |
| Mutations | Flag visible only | Require `allow_mutations=True` (Experimental) |
| Pin | `>=0.1.0,<0.2` | `>=0.2.0,<0.3` |
| SDK | none | Official `mcp>=1.9.0,<2` |

## Fixture expectations

1. Disabled projection still lists zero tools/resources after upgrade.
2. Enabled + zero registrations mounts an empty MCP surface (no ambient projection).
3. Existing `check_authz(principal=..., action=...)` calls continue to fail closed
   without a principal.
4. Consumers that relied on marker-only mount without HTTP continue to work when
   the host app lacks Starlette routes; FastAPI hosts gain `/mcp` POST.

## Unsupported client capabilities

Clients advertising unknown capability keys are accepted; Hedron ignores the
unknown keys and never widens authority (see `UNSUPPORTED_CAPABILITY_BEHAVIOR`
in `hedron_mcp.compat`).
