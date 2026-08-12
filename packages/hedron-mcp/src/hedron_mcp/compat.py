"""Pinned MCP protocol / SDK compatibility matrix (PROTOCOL-032)."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

# Protocol revisions Hedron negotiates on Supported Streamable HTTP.
SUPPORTED_PROTOCOL_VERSIONS: tuple[str, ...] = (
    "2024-11-05",
    "2025-03-26",
)
DEFAULT_PROTOCOL_VERSION = "2025-03-26"

# Official Python SDK pin (see packages/hedron-mcp/pyproject.toml).
SDK_DISTRIBUTION = "mcp"
SDK_PIN = ">=1.9.0,<2"

# Documented Supported MCP clients for PROTOCOL-032 evidence.
SUPPORTED_CLIENTS: tuple[str, ...] = (
    "cursor",
    "claude-desktop",
    "mcp-python-sdk",
)

UNSUPPORTED_CAPABILITY_BEHAVIOR = (
    "Unsupported client capabilities are ignored; Hedron continues with the "
    "intersection of Supported protocol features and never widens authority."
)


def sdk_version() -> str:
    """Return the installed official ``mcp`` SDK version string."""
    try:
        return version(SDK_DISTRIBUTION)
    except PackageNotFoundError as exc:  # pragma: no cover - env misconfig
        raise RuntimeError(f"official MCP SDK ({SDK_DISTRIBUTION} {SDK_PIN}) is required") from exc


def negotiate_protocol_version(requested: str | None) -> str:
    """Return a Supported protocol version or the default."""
    if requested and requested in SUPPORTED_PROTOCOL_VERSIONS:
        return requested
    return DEFAULT_PROTOCOL_VERSION
