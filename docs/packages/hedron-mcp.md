# hedron-mcp

Deny-by-default MCP Streamable HTTP projection for Hedron.

**Package maturity:** Beta (`0.2.1`) · pin `>=0.2.1,<0.3` (compatible floor `>=0.2.0,<0.3`)  
**Flagship extra:** `hedron[mcp]` · **Import:** `hedron_mcp`  
Living Hedron train `0.59.x` (checkout tip `v0.59.0`; flagship extra install from PyPI
stays `>=0.58.0,<0.60` ). Disabled and empty until resources and tools are
**explicitly registered**. MCP never grants authority beyond the authenticated principal.

Production-grade for the declared Supported inventory (phase **0.32** /
[RFC-0065](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0065-PRODUCTION-GRADE-MCP.md) / D-060). Mutating tools remain
**Experimental** and require `allow_mutations=True`.

## Install

```bash
pip install "hedron[mcp]>=0.58.0,<0.60"
# or
pip install "hedron-mcp>=0.2.0,<0.3"
```

Installing without registrations remains a no-op empty server.

## When to use

- Deny-by-default MCP tool/resource projection from a Hedron FastAPI app
- Explicit, principal-bounded agent tool surfaces with app-owned authz/tenant hooks

Prefer leaving `enabled=False` (default) until registrations are intentional.

## Quick start

```python
import os
from hedron import Hedron
from hedron_mcp import McpProjection, McpResource, McpTool, mount_mcp

app = Hedron(
    title="MCP demo",
    security="standard",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

# Prefer session / host auth. Do not trust client headers unless a reverse
# proxy overwrites them; the default resolver never reads x-hedron-principal.
projection = McpProjection(
    enabled=True,
    principal_resolver=lambda request: request.session.get("user"),
)
projection.register_resource(McpResource(uri="hedron://page/home", name="home"))
projection.register_tool(
    McpTool(
        name="status",
        schema={"type": "object", "properties": {}},
        mutate=False,
        handler=lambda: {"ok": True},
    )
)
mount_mcp(app, projection)  # Streamable HTTP at POST /mcp
```

See [STABILITY](../api/STABILITY.md), [RELEASE_0_32](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_32.md), and
[upgrade fixtures](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/upgrade-fixtures-032.md).
