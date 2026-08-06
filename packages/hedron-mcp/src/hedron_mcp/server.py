"""MCP projection: disabled and empty until explicit opt-in registration."""

from __future__ import annotations

import contextlib
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "AuthorizationError",
    "McpProjection",
    "McpResource",
    "McpTool",
    "mount_mcp",
]


class AuthorizationError(PermissionError):
    """Raised when MCP authz fails closed (missing principal or overreach)."""


@dataclass(frozen=True, slots=True)
class McpResource:
    """Opt-in MCP resource (pages, component metadata, data descriptions)."""

    uri: str
    name: str
    description: str = ""
    mime_type: str = "application/json"
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class McpTool:
    """Opt-in MCP tool wrapping an explicit action or typed function."""

    name: str
    schema: Mapping[str, Any]
    mutate: bool
    handler: Callable[..., Any]
    description: str = ""


@dataclass
class McpProjection:
    """Deny-by-default MCP projection surface.

    Defaults to ``enabled=False`` with empty resources and tools. Discovery
    returns empty lists while disabled. Enabling MCP never auto-exposes routes.
    """

    enabled: bool = False
    _resources: dict[str, McpResource] = field(default_factory=dict, init=False, repr=False)
    _tools: dict[str, McpTool] = field(default_factory=dict, init=False, repr=False)

    @property
    def resources(self) -> tuple[McpResource, ...]:
        if not self.enabled:
            return ()
        return tuple(self._resources.values())

    @property
    def tools(self) -> tuple[McpTool, ...]:
        if not self.enabled:
            return ()
        return tuple(self._tools.values())

    def register_resource(self, resource: McpResource) -> None:
        if resource.uri in self._resources:
            raise ValueError(f"MCP resource already registered: {resource.uri!r}")
        self._resources[resource.uri] = resource

    def register_tool(self, tool: McpTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"MCP tool already registered: {tool.name!r}")
        self._tools[tool.name] = tool

    def list_resources(self) -> list[McpResource]:
        """Return registered resources, or empty when disabled."""
        if not self.enabled:
            return []
        return list(self._resources.values())

    def list_tools(self) -> list[McpTool]:
        """Return registered tools, or empty when disabled."""
        if not self.enabled:
            return []
        return list(self._tools.values())

    def check_authz(
        self,
        *,
        principal: str | None,
        action: str,
        resource: str | None = None,
        scopes: Mapping[str, Any] | None = None,
    ) -> None:
        """Principal-bounded authz stub: require a principal; never exceed it.

        MCP never grants authority beyond the authenticated principal. A missing
        principal fails closed. Declared scopes may only subset the principal's
        own identity (no elevation).
        """
        if not principal:
            raise AuthorizationError(
                "MCP authorization requires an authenticated principal; deny-by-default."
            )
        if scopes:
            claimed = scopes.get("principal")
            if claimed is not None and claimed != principal:
                raise AuthorizationError(
                    "MCP authorization never exceeds the authenticated principal."
                )
            allowed = scopes.get("allowed_principals")
            if allowed is not None and principal not in allowed:
                raise AuthorizationError(
                    "MCP authorization never exceeds the authenticated principal."
                )
        # Action/resource are recorded for future audit wiring; stub always
        # admits after principal identity checks succeed.
        _ = (action, resource)


def mount_mcp(app: Any, projection: McpProjection) -> None:
    """Mount Streamable HTTP MCP routes on ``app``.

    No-ops when ``projection.enabled`` is false so installing the package without
    enabling remains an empty server.
    """
    if not projection.enabled:
        return
    # Full Streamable HTTP transport lands with conformance evidence; enabling
    # without a transport implementation still fails closed for discovery via
    # list_* while registration APIs remain available for application wiring.
    marker = getattr(app, "state", None)
    if marker is not None:
        with contextlib.suppress(Exception):
            marker.hedron_mcp = projection
