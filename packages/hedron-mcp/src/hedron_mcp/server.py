"""MCP projection: disabled and empty until explicit opt-in registration."""

from __future__ import annotations

import inspect
import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

from hedron_mcp.audit import McpAuditLog
from hedron_mcp.bounds import BoundsError, McpBounds
from hedron_mcp.compat import SDK_PIN, sdk_version

__all__ = [
    "AuthorizationError",
    "BoundsError",
    "InvalidParamsError",
    "McpBounds",
    "McpProjection",
    "McpResource",
    "McpTool",
    "mount_mcp",
]

PrincipalResolver = Callable[[Any], str | None]
AuthzHook = Callable[..., None]
TenantHook = Callable[..., None]
ResourceReader = Callable[[str, str | None], Mapping[str, Any] | str]


class AuthorizationError(PermissionError):
    """Raised when MCP authz fails closed (missing principal or overreach)."""


class InvalidParamsError(ValueError):
    """Raised when tool arguments fail the advertised JSON Schema (-32602)."""


@dataclass(frozen=True, slots=True)
class McpResource:
    """Opt-in MCP resource (pages, component metadata, data descriptions)."""

    uri: str
    name: str
    description: str = ""
    mime_type: str = "application/json"
    metadata: Mapping[str, Any] = field(default_factory=dict)
    reader: ResourceReader | None = None


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
    returns empty lists while disabled. Enabling MCP never auto-exposes routes
    until ``mount_mcp`` attaches Streamable HTTP.
    """

    enabled: bool = False
    allow_mutations: bool = False
    package_version: str = "0.2.0"
    principal_resolver: PrincipalResolver | None = None
    authz_hook: AuthzHook | None = None
    tenant_hook: TenantHook | None = None
    allowed_origins: frozenset[str] | None = None
    bounds: McpBounds = field(default_factory=McpBounds)
    audit: McpAuditLog = field(default_factory=McpAuditLog)
    _resources: dict[str, McpResource] = field(default_factory=dict, init=False, repr=False)
    _tools: dict[str, McpTool] = field(default_factory=dict, init=False, repr=False)
    _mounted: bool = field(default=False, init=False, repr=False)

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
        self._assert_safe_uri(resource.uri)
        if resource.uri in self._resources:
            raise ValueError(f"MCP resource already registered: {resource.uri!r}")
        self._resources[resource.uri] = resource
        self.audit.emit(
            code="HED-MCP-REGISTER-RESOURCE",
            kind="registration",
            principal=None,
            detail={"uri": resource.uri, "name": resource.name},
        )

    def register_tool(self, tool: McpTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"MCP tool already registered: {tool.name!r}")
        self._tools[tool.name] = tool
        self.audit.emit(
            code="HED-MCP-REGISTER-TOOL",
            kind="registration",
            principal=None,
            detail={"name": tool.name, "mutate": tool.mutate},
        )

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

    def resolve_principal(self, request: Any) -> str | None:
        """Reuse host authentication; never invent an IdP.

        Default identity comes only from an authenticated session when
        ``SessionMiddleware`` (or equivalent) has installed ``scope["session"]``.
        Client-controlled headers such as ``x-hedron-principal`` / ``x-user`` are
        never trusted unless the host supplies an explicit ``principal_resolver``.
        """
        if self.principal_resolver is not None:
            return self.principal_resolver(request)
        # Starlette's Request.session asserts when middleware is absent; only read
        # the session when the scope extension is present.
        scope = getattr(request, "scope", None)
        if not isinstance(scope, Mapping) or "session" not in scope:
            return None
        session = request.session
        if isinstance(session, Mapping):
            for key in ("user", "username", "principal", "sub"):
                value = session.get(key)
                if value:
                    return str(value)
        return None

    def check_authz(
        self,
        *,
        principal: str | None,
        action: str,
        resource: str | None = None,
        scopes: Mapping[str, Any] | None = None,
        tenant_id: str | None = None,
    ) -> None:
        """Principal-bounded authz: require a principal; never exceed it.

        Application-owned ``authz_hook`` / ``tenant_hook`` run after identity
        checks and must fail closed. UI option filtering is not authorization.
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
        if self.authz_hook is not None:
            self.authz_hook(
                principal=principal,
                action=action,
                resource=resource,
                scopes=scopes,
                tenant_id=tenant_id,
            )
        if self.tenant_hook is not None:
            self.tenant_hook(
                principal=principal,
                action=action,
                resource=resource,
                tenant_id=tenant_id,
            )
        self.audit.emit(
            code="HED-MCP-AUTHZ-OK",
            kind="authorization",
            principal=principal,
            detail={"action": action, "resource": resource, "tenant_id": tenant_id},
        )

    def authorize(
        self,
        *,
        principal: str | None,
        action: str,
        resource: str | None = None,
        scopes: Mapping[str, Any] | None = None,
        tenant_id: str | None = None,
    ) -> None:
        self.check_authz(
            principal=principal,
            action=action,
            resource=resource,
            scopes=scopes,
            tenant_id=tenant_id,
        )

    def read_resource(self, uri: str, *, principal: str | None) -> dict[str, Any]:
        self._assert_safe_uri(uri)
        if not self.enabled:
            raise KeyError(uri)
        resource = self._resources.get(uri)
        if resource is None:
            raise KeyError(uri)
        if resource.reader is not None:
            payload = resource.reader(uri, principal)
        else:
            payload = {
                "uri": resource.uri,
                "name": resource.name,
                "description": resource.description,
                "metadata": dict(resource.metadata),
            }
        if isinstance(payload, str):
            text = payload
            mime = resource.mime_type
        else:
            text = payload.get("text")  # type: ignore[assignment]
            if text is None:
                text = json.dumps(dict(payload), default=str)
            mime = str(payload.get("mimeType") or resource.mime_type)
        return {"text": str(text), "mimeType": mime}

    def call_tool(
        self,
        name: str,
        arguments: Mapping[str, Any],
        *,
        principal: str | None,
    ) -> Any:
        if not self.enabled:
            raise KeyError(name)
        tool = self._tools.get(name)
        if tool is None:
            raise KeyError(name)
        if tool.mutate and not self.allow_mutations:
            raise AuthorizationError(
                "Mutating MCP tools require explicit allow_mutations=True "
                "(Experimental; excluded from Supported inventory)."
            )
        validated = self._validate_tool_arguments(tool, arguments)
        try:
            result = tool.handler(**validated) if validated else tool.handler()
        except TypeError as exc:
            raise InvalidParamsError(f"Invalid arguments for tool {name!r}: {exc}") from exc
        if inspect.isawaitable(result):
            raise TypeError("async MCP tool handlers are not Supported; await in the host")
        return result

    @staticmethod
    def _validate_tool_arguments(
        tool: McpTool, arguments: Mapping[str, Any]
    ) -> dict[str, Any]:
        """Enforce the advertised ``inputSchema`` before invoking the handler (#177)."""
        payload = dict(arguments)
        schema = tool.schema
        if not schema:
            return payload
        try:
            from jsonschema import Draft202012Validator
            from jsonschema.exceptions import SchemaError, ValidationError
        except ImportError as exc:  # pragma: no cover - mcp pins jsonschema
            raise RuntimeError(
                "jsonschema is required to validate MCP tool arguments"
            ) from exc
        try:
            validator = Draft202012Validator(dict(schema))
            errors = sorted(validator.iter_errors(payload), key=lambda e: list(e.path))
        except SchemaError as exc:
            raise InvalidParamsError(
                f"Tool {tool.name!r} has an invalid inputSchema: {exc.message}"
            ) from exc
        if errors:
            first = errors[0]
            path = ".".join(str(p) for p in first.path) or "(root)"
            raise InvalidParamsError(
                f"Invalid arguments for tool {tool.name!r} at {path}: {first.message}"
            )
        return payload

    @staticmethod
    def _assert_safe_uri(uri: str) -> None:
        parsed = urlparse(uri)
        if parsed.scheme in {"file", "http", "https", "ftp", "data"}:
            raise AuthorizationError(
                f"MCP resource URI scheme {parsed.scheme!r} is excluded "
                "(no arbitrary filesystem/URL projection)."
            )
        if ".." in uri or uri.startswith("/"):
            raise AuthorizationError("MCP resource URI path traversal is denied.")


def mount_mcp(app: Any, projection: McpProjection, *, path: str = "/mcp") -> None:
    """Mount Streamable HTTP MCP routes on ``app``.

    No-ops when ``projection.enabled`` is false so installing the package without
    enabling remains an empty server. Zero registrations still mounts an empty
    JSON-RPC surface that lists nothing and grants no ambient authority.
    """
    if not projection.enabled:
        return
    # Prove SDK pin is importable for PROTOCOL-032 matrix honesty.
    _ = sdk_version()
    _ = SDK_PIN
    projection.bounds.assert_worker_safe()
    marker = getattr(app, "state", None)
    if marker is not None:
        marker.hedron_mcp = projection
    if hasattr(app, "router") or hasattr(app, "routes"):
        from hedron_mcp.transport import mount_streamable_http

        mount_streamable_http(app, projection, path=path)
        projection._mounted = True
    else:
        # Non-ASGI hosts / unit fixtures may attach the projection marker only.
        projection._mounted = False
    projection.audit.emit(
        code="HED-MCP-MOUNT",
        kind="registration",
        principal=None,
        detail={"path": path, "sdk": sdk_version(), "http_mounted": projection._mounted},
    )
