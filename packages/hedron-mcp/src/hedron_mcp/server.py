"""MCP projection: disabled and empty until explicit opt-in registration."""

from __future__ import annotations

import inspect
import json
import unicodedata
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from urllib.parse import unquote, urlparse

from hedron_core.typing_aliases import JsonObject, JsonValue
from hedron_mcp.audit import McpAuditLog
from hedron_mcp.bounds import BoundsError, McpBounds
from hedron_mcp.compat import SDK_PIN, sdk_version


def _package_version() -> str:
    from importlib.metadata import PackageNotFoundError, version

    try:
        return version("hedron-mcp")
    except PackageNotFoundError:
        return "0.2.1"


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

PrincipalResolver = Callable[[object], str | None]
AuthzHook = Callable[..., None]
TenantHook = Callable[..., None]
ResourceReader = Callable[[str, str | None], Mapping[str, JsonValue] | str]

# Deny-by-default: only the documented Hedron resource URI scheme is Supported.
_ALLOWED_RESOURCE_URI_SCHEMES = frozenset({"hedron"})
_URI_DECODE_ROUNDS = 3


def _percent_decode_uri(uri: str) -> str:
    decoded = uri
    for _ in range(_URI_DECODE_ROUNDS):
        next_decoded = unquote(decoded)
        if next_decoded == decoded:
            break
        decoded = next_decoded
    return decoded


def _uri_has_traversal(candidate: str) -> bool:
    candidate = unicodedata.normalize("NFKC", candidate)
    lowered = candidate.lower()
    if "%2e%2e" in lowered or "%2e." in lowered or ".%2e" in lowered:
        return True
    if ".." in candidate or candidate.startswith("/"):
        return True
    path = urlparse(candidate).path.replace(";", "/")
    parts = [p for p in path.split("/") if p not in {"", "."}]
    return any(part == ".." or part.startswith("..") for part in parts)


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
    metadata: Mapping[str, JsonValue] = field(default_factory=dict)
    reader: ResourceReader | None = None
    authorize: AuthzHook | None = None


@dataclass(frozen=True, slots=True)
class McpTool:
    """Opt-in MCP tool wrapping an explicit action or typed function."""

    name: str
    schema: Mapping[str, JsonValue]
    mutate: bool
    handler: Callable[..., object]
    description: str = ""
    authorize: AuthzHook | None = None


@dataclass
class McpProjection:
    """Deny-by-default MCP projection surface.

    Defaults to ``enabled=False`` with empty resources and tools. Discovery
    returns empty lists while disabled. Enabling MCP never auto-exposes routes
    until ``mount_mcp`` attaches Streamable HTTP.
    """

    enabled: bool = False
    allow_mutations: bool = False
    package_version: str = field(default_factory=_package_version)
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

    def unregister_resource(self, uri: str) -> None:
        self._resources.pop(uri, None)

    def unregister_tool(self, name: str) -> None:
        self._tools.pop(name, None)

    def consume_catalog(self, catalog: object) -> tuple[str, ...]:
        """Read catalog logical ids. Does not enable MCP or register tools."""
        entries = getattr(catalog, "entries", {}) or {}
        ids = tuple(sorted(str(key) for key in entries))
        self.audit.emit(
            code="HED-MCP-CATALOG-CONSUME",
            kind="registration",
            principal=None,
            detail={"count": len(ids), "enabled": self.enabled, "exposure": False},
        )
        return ids

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

    def resolve_principal(self, request: object) -> str | None:
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
        session = getattr(request, "session", None)
        if isinstance(session, Mapping):
            for key in ("user", "username", "principal", "sub"):
                value = session.get(key)
                if isinstance(value, str) and value.strip():
                    return value
        return None

    def check_authz(
        self,
        *,
        principal: str | None,
        action: str,
        resource: str | None = None,
        scopes: Mapping[str, JsonValue] | None = None,
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
            if allowed is not None and principal not in allowed:  # type: ignore[operator]
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
        item_hook = self._authorize_for_resource(resource)
        if item_hook is not None and item_hook is not self.authz_hook:
            item_hook(
                principal=principal,
                action=action,
                resource=resource,
                scopes=scopes,
                tenant_id=tenant_id,
            )
        if (
            action in {"tools/call", "resources/read"}
            and resource is not None
            and self.authz_hook is None
            and item_hook is None
        ):
            raise AuthorizationError(
                "MCP authorization requires an authz_hook or per-item authorize; deny-by-default."
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

    def _authorize_for_resource(self, resource: str | None) -> AuthzHook | None:
        if not resource:
            return None
        tool = self._tools.get(resource)
        if tool is not None:
            return tool.authorize
        rec = self._resources.get(resource)
        if rec is not None:
            return rec.authorize
        return None

    def authorize(
        self,
        *,
        principal: str | None,
        action: str,
        resource: str | None = None,
        scopes: Mapping[str, JsonValue] | None = None,
        tenant_id: str | None = None,
    ) -> None:
        self.check_authz(
            principal=principal,
            action=action,
            resource=resource,
            scopes=scopes,
            tenant_id=tenant_id,
        )

    def read_resource(self, uri: str, *, principal: str | None) -> JsonObject:
        self.authorize(principal=principal, action="resources/read", resource=uri)
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
        arguments: Mapping[str, JsonValue],
        *,
        principal: str | None,
    ) -> object:
        self.authorize(principal=principal, action="tools/call", resource=name)
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
        tool: McpTool, arguments: Mapping[str, JsonValue]
    ) -> dict[str, JsonValue]:
        """Enforce the advertised ``inputSchema`` before invoking the handler (#177)."""
        payload = dict(arguments)
        schema = tool.schema
        if not schema:
            return payload
        try:
            from jsonschema import Draft202012Validator
            from jsonschema.exceptions import SchemaError
        except ImportError as exc:  # pragma: no cover - mcp pins jsonschema
            raise RuntimeError("jsonschema is required to validate MCP tool arguments") from exc
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
        if not uri or uri.strip() != uri:
            raise AuthorizationError("MCP resource URI is empty or not canonical.")
        if "\\" in uri or any(ord(ch) < 32 for ch in uri):
            raise AuthorizationError("MCP resource URI path traversal is denied.")
        decoded = _percent_decode_uri(uri)
        if "\\" in decoded or any(ord(ch) < 32 for ch in decoded):
            raise AuthorizationError("MCP resource URI path traversal is denied.")
        if _uri_has_traversal(uri) or _uri_has_traversal(decoded):
            raise AuthorizationError("MCP resource URI path traversal is denied.")
        scheme = (urlparse(decoded).scheme or urlparse(uri).scheme).lower()
        if scheme not in _ALLOWED_RESOURCE_URI_SCHEMES:
            raise AuthorizationError(
                f"MCP resource URI scheme {scheme!r} is excluded "
                "(no arbitrary filesystem/URL projection)."
            )


def mount_mcp(app: object, projection: McpProjection, *, path: str = "/mcp") -> None:
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
