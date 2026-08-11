# hedron-mcp

Deny-by-default MCP Streamable HTTP projection for Hedron.

**Package maturity:** Experimental Alpha (`0.1.x`) · pin `>=0.1.0,<0.2`  
**Flagship extra:** `hedron[mcp]` · **Import:** `hedron_mcp`  
Disabled and empty until resources and tools are **explicitly registered**. MCP
never grants authority beyond the authenticated principal.

**Not** a Supported production surface — see
[What’s ready](../guides/whats-ready.md).

## Install

```bash
pip install "hedron[mcp]>=0.28.1,<0.29"
# or
pip install "hedron-mcp>=0.1.0,<0.2"
```

Installing without registrations remains a no-op empty server.

## When to use

- Experimenting with MCP tool/resource projection from a Hedron FastAPI app
- Explicit, deny-by-default agent tool surfaces

Do **not** enable in production without your own authz review. Prefer leaving
`enabled=False` (default) until registrations are intentional.

## Quick start

```python
from hedron import Hedron
from hedron_mcp import McpProjection, McpResource, McpTool, mount_mcp

app = Hedron(
    title="MCP demo",
    security="standard",
    session_secret="dev-only",
    explorer="off",
)

proj = McpProjection(enabled=True)
proj.register_resource(McpResource(uri="hedron://pages/home", name="home"))
proj.register_tool(McpTool(name="ping", schema={}, mutate=False, handler=lambda: {"ok": True}))
mount_mcp(app, proj)
```

## Surfaces

| Symbol | Role |
|---|---|
| `McpProjection` | Deny-by-default registry (`enabled=False` by default) |
| `McpResource` / `McpTool` | Explicit registrations |
| `mount_mcp(app, projection)` | Attach projection to a Hedron / FastAPI app |
| `AuthorizationError` | Fail-closed authorization signal |

## Errors and failure modes

| Condition | Behavior |
|---|---|
| `enabled=False` (default) | Empty / inert — no tools exposed |
| Unauthenticated or unauthorized principal | Fail closed (`AuthorizationError`) |
| Expecting auto-published app callables | Out of scope — registration is explicit only |

## Related docs

- [What’s ready](../guides/whats-ready.md)
- [Stability](../api/STABILITY.md)
- [Inference / model demos](../api/INFERENCE.md) (related agent surfaces)

## Links

- [PyPI](https://pypi.org/project/hedron-mcp/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-mcp/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-mcp)
