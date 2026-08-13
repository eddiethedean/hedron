# Upgrade to Hedron 0.32

This guide covers an application upgrade onto the **0.32.x** train
(current tip **`v0.32.0`**). New applications should use
[Build your first app](../getting-started/quickstart.md).

## Summary

Hedron 0.32.x graduates **`hedron-mcp`** to production-grade deny-by-default MCP
projection (D-060 / RFC-0065): authenticated Streamable HTTP for an explicitly
bounded Supported inventory. Install and mount grant no ambient authority.
Mutating tools remain Experimental (`allow_mutations=True`).

Prior trains remain in force: Workbench (`hedron-workbench` / `fastapi-workbench`),
tooling-grade conformance packages, and `hedron migrate streamlit` from 0.29–0.31.
No Supported CRUD/admin API removal is listed. Polling remains the production
recommendation for live status. SSE, WebSocket, streaming, and navigation preload
remain experimental. Flask/Django adapters are untouched.

## Before upgrading

1. Commit or back up your lockfile.
2. Confirm you are on a recent pin (`hedron>=0.28.2,<0.29` through `>=0.31.0,<0.32`,
   or the tip pin already).
3. If you use Alpha `hedron-mcp` `0.1.x`, plan to re-register tools/resources and
   stop relying on client-controlled identity headers — principals come from the
   authenticated session or an explicit host `principal_resolver`.
4. If you deploy on Posit Workbench, keep `hedron[workbench]` and the
   `hedron-workbench run` launch command (unchanged by 0.32).

## Install

```bash
python -m pip install -U "hedron>=0.32.0,<0.33"
# Optional MCP:
python -m pip install -U "hedron[mcp]>=0.32.0,<0.33"
# or
python -m pip install -U "hedron-mcp>=0.2.0,<0.3"
```

Workbench sessions (unchanged):

```bash
python -m pip install -U "hedron[workbench]>=0.32.0,<0.33"
hedron-workbench run app:app
```

## After upgrading

1. Run your test suite and a smoke path through login → HTMX fragment → logout.
2. If you mount MCP, confirm `enabled=True` only with explicit registrations and
   host authn; verify DELETE `/mcp` and cancel behavior under your reverse proxy.
3. Prefer [polling](live-interaction.md) for live job status unless you accept
   experimental SSE/WebSocket risk.

See [What’s new in 0.32](whats-new-0.32.md) · [What’s ready](whats-ready.md) ·
[hedron-mcp](../packages/hedron-mcp.md).
