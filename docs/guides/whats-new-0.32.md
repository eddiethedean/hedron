# What’s new in 0.32

!!! note "Living train"

    Pin `hedron>=0.40.0,<0.41` for new apps. See [What’s new in 0.40](whats-new-0.40.md).

**Published** as `v0.32.0`. Historical pin for this train: `hedron>=0.32.0,<0.33`.

Phase **0.32** (D-060 / RFC-0065) graduates **`hedron-mcp`** to production-grade
deny-by-default MCP Streamable HTTP projection for an explicitly bounded Supported
inventory. Install and mount grant no ambient authority.

## Highlights

- **`hedron-mcp` `0.2.0` Beta:** deny-by-default Streamable HTTP mount; explicit
  resource/tool registration; host authn reuse; app-owned authz/tenant hooks;
  bounds, redacted audit, cancel, and multi-worker-safe lifecycle.
- **Supported inventory only:** mutating tools stay **Experimental** and require
  `allow_mutations=True`; vendor-specific extensions remain out of scope.
- **Coordinated train:** `hedron` / core packages `0.32.0`; MCP remains an
  independent satellite (`>=0.2.0,<0.3`), not train-locked `0.32.0` and not `1.0.0`.
- **Hardening on the cut:** session-only default principal resolution (#168);
  spreadsheet formula evasion strip (#169); optional-session scope gates (#170);
  MCP cancel by client request id (#171); bounded MCP maps (#172); DELETE closes
  MCP sessions with server-minted ids (#173).

## Upgrade

```bash
python -m pip install -U "hedron>=0.34.0,<0.35"
# Optional MCP projection:
python -m pip install -U "hedron[mcp]>=0.32.0,<0.33"
# or
python -m pip install -U "hedron-mcp>=0.2.0,<0.3"
```

From Alpha `hedron-mcp` `0.1.x`: re-register tools/resources explicitly; do not rely
on client-controlled identity headers — principals come from the authenticated
session or an explicit host `principal_resolver`.

Details: [RELEASE_0_32](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_32.md) · [upgrade guide](upgrade.md) ·
[hedron-mcp](../packages/hedron-mcp.md).
