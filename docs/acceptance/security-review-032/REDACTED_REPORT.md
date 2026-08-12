# REVIEW-032 redacted security review report

**Gate:** REVIEW-032  
**Baseline:** Published `v0.31.0`; Alpha `hedron-mcp` `0.1.x`  
**Package at cut:** `hedron-mcp` `0.2.0` Beta (Supported inventory)  
**Methodology:** Maintainer-led structured review independent of the feature-authoring
pass, plus `tests/security/test_mcp_adversarial.py`.

## Summary

No unresolved **critical** or **high** findings remain for the declared Supported
deny-by-default MCP inventory. Mutating tools without `allow_mutations=True` stay
Experimental and are fail-closed.

## Trust boundary findings (redacted)

1. **Deny-by-default empty mount** — disabled projections do not mount HTTP;
   enabled zero-registration mounts list empty tools/resources.
2. **Confused deputy** — scope principal elevation is rejected; tools cannot widen
   beyond the authenticated principal.
3. **Cross-tenant observation** — application `tenant_hook` fails closed across
   tenants.
4. **Identifier enumeration** — unknown resource URIs return JSON-RPC not-found
   without leaking sibling identifiers.
5. **Exfiltration via URI schemes** — `file`/`http`/`https` resource URIs are
   excluded from Supported registration.
6. **Origin allowlist** — optional `allowed_origins` blocks foreign Origins.
7. **Mutation enablement** — `mutate=True` tools require explicit Experimental
   `allow_mutations=True`.
8. **Audit redaction** — secret-shaped keys are redacted from structured audit
   payloads (`HED-MCP-*`).

## Residual accepted risks

- Process-local audit buffers are not durable across workers; operators must attach
  an external sink when multi-worker evidence requires centralized audit.
- Official `mcp` SDK is pinned for PROTOCOL matrix honesty; Hedron owns the
  Streamable HTTP JSON-RPC surface and authz policy.

## Disposition

See `DISPOSITION.toml` (`critical_high_open = false`).
