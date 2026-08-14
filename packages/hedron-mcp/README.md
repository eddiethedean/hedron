# hedron-mcp

[![PyPI](https://img.shields.io/pypi/v/hedron-mcp.svg)](https://pypi.org/project/hedron-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/hedron-mcp.svg)](https://pypi.org/project/hedron-mcp/)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

Deny-by-default MCP Streamable HTTP projection for Hedron.

Disabled and empty until resources and tools are explicitly registered. MCP
never grants authority beyond the authenticated principal. Installing the
package without registrations remains a no-op empty server.

Also available as the flagship extra `hedron[mcp]`.

**Package maturity:** Beta (`0.2.x`) · pin `>=0.2.0,<0.3`

Production-grade for the declared Supported inventory (phase 0.32 / RFC-0065).
Mutating tools remain Experimental (`allow_mutations=True`).

## Install

```bash
pip install "hedron-mcp>=0.2.0,<0.3"
# or
uv add "hedron-mcp>=0.2.0,<0.3"
# via flagship:
pip install "hedron[mcp]>=0.37.0,<0.38"
```

Requires Python 3.11–3.14.

## Quick start

```python
from hedron import Hedron
from hedron_mcp import McpProjection, McpResource, McpTool, mount_mcp

app = Hedron(
    title="MCP demo",
    security="standard",
    session_secret="dev-only",
)

# Prefer session / host auth. Header identity is host-owned opt-in only —
# the default resolver never trusts x-hedron-principal / x-user.
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
mount_mcp(app, projection)
```

## License

MIT
