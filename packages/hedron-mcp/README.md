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

**Package maturity:** Experimental Alpha (`0.1.x`) · pin `>=0.1.0,<0.2` and expect churn

Not a Supported production surface — see
[What’s ready](https://hedron.readthedocs.io/en/latest/guides/whats-ready/).

## Install

```bash
pip install "hedron-mcp>=0.1.0,<0.2"
# or
uv add "hedron-mcp>=0.1.0,<0.2"
# via flagship:
pip install "hedron[mcp]>=0.27.0,<0.28"
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
    explorer="off",
)

proj = McpProjection(enabled=True)
proj.register_resource(McpResource(uri="hedron://pages/home", name="home"))
proj.register_tool(McpTool(name="ping", schema={}, mutate=False, handler=lambda: {"ok": True}))
mount_mcp(app, proj)
```

With `enabled=False` (the default), registration and mount stay inert.

## Public API

| Symbol | Role |
|---|---|
| `McpProjection` | Deny-by-default registry (`enabled=False` by default) |
| `McpResource` / `McpTool` | Explicit registrations |
| `mount_mcp(app, projection)` | Attach projection to a Hedron/FastAPI app |
| `AuthorizationError` | Fail-closed authorization signal |

## Links

- [Package docs](https://hedron.readthedocs.io/en/latest/packages/hedron-mcp/)
- [What’s ready](https://hedron.readthedocs.io/en/latest/guides/whats-ready/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-mcp/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-mcp)
- [Issues](https://github.com/eddiethedean/hedron/issues)
- [`hedron`](https://pypi.org/project/hedron/)

## License

MIT. See the [repository license](https://github.com/eddiethedean/hedron/blob/main/LICENSE).
