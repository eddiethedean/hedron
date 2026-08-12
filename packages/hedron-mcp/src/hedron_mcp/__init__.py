"""Deny-by-default MCP Streamable HTTP projection for Hedron."""

from __future__ import annotations

from hedron_mcp.audit import McpAuditEvent, McpAuditLog, redact_value
from hedron_mcp.bounds import BoundsError, McpBounds
from hedron_mcp.compat import (
    DEFAULT_PROTOCOL_VERSION,
    SDK_PIN,
    SUPPORTED_CLIENTS,
    SUPPORTED_PROTOCOL_VERSIONS,
    negotiate_protocol_version,
    sdk_version,
)
from hedron_mcp.server import (
    AuthorizationError,
    McpProjection,
    McpResource,
    McpTool,
    mount_mcp,
)

__version__ = "0.2.0"

__all__ = [
    "AuthorizationError",
    "BoundsError",
    "DEFAULT_PROTOCOL_VERSION",
    "McpAuditEvent",
    "McpAuditLog",
    "McpBounds",
    "McpProjection",
    "McpResource",
    "McpTool",
    "SDK_PIN",
    "SUPPORTED_CLIENTS",
    "SUPPORTED_PROTOCOL_VERSIONS",
    "__version__",
    "mount_mcp",
    "negotiate_protocol_version",
    "redact_value",
    "sdk_version",
]
