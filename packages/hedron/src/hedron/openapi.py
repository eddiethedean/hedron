"""OpenAPI post-processing for Hedron HTML routes."""

from __future__ import annotations

from typing import cast

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from hedron_core.registry import get_registry
from hedron_core.scopes import RequiresScopes
from hedron_core.typing_aliases import JsonObject, JsonValue
from hedron_core.updates import list_handle_descriptors

__all__ = ["install_openapi", "operation_id_for"]


def operation_id_for(kind: str, name: str, path: str, method: str) -> str:
    cleaned_path = path.strip("/").replace("/", "_").replace("{", "").replace("}", "") or "root"
    return f"hedron_{kind}_{name}_{method.lower()}_{cleaned_path}"


def install_openapi(app: FastAPI) -> None:
    def custom_openapi() -> JsonObject:
        if app.openapi_schema is not None:
            return cast(JsonObject, app.openapi_schema)
        schema = cast(
            JsonObject,
            get_openapi(
                title=app.title,
                version=app.version,
                description=app.description,
                routes=app.routes,
            ),
        )
        registry = get_registry()
        route_by_op = {r.operation_id: r for r in registry.routes()}
        handles = getattr(getattr(app, "state", None), "hedron_handles", None)
        handle_map = cast(dict[str, object], handles) if isinstance(handles, dict) else {}
        descriptors = {item.logical_id: item for item in list_handle_descriptors()}
        needs_hedron_scopes = False
        paths = schema.get("paths")
        if isinstance(paths, dict):
            for path_item in paths.values():
                if not isinstance(path_item, dict):
                    continue
                typed_path_item = cast(dict[str, JsonValue], path_item)
                for operation_value in typed_path_item.values():
                    if not isinstance(operation_value, dict):
                        continue
                    operation = cast(dict[str, JsonValue], operation_value)
                    op_id = operation.get("operationId")
                    meta = route_by_op.get(op_id) if isinstance(op_id, str) else None
                    if meta is None:
                        continue
                    operation.setdefault("x-hedron-kind", meta.kind)
                    operation.setdefault("x-hedron-logical-id", meta.logical_id)
                    entry = None
                    catalog = getattr(app.state, "hedron_interactions", None)
                    if catalog is not None:
                        getter = getattr(catalog, "get", None)
                        if callable(getter):
                            entry = getter(meta.logical_id)
                    if entry is not None:
                        operation.setdefault(
                            "x-hedron-descriptor-fingerprint",
                            getattr(entry, "descriptor_fingerprint", None),
                        )
                        if getattr(entry, "type_schema_fingerprint", None):
                            operation.setdefault(
                                "x-hedron-type-schema-fingerprint",
                                getattr(entry, "type_schema_fingerprint", None),
                            )
                    if meta.htmx_inference:
                        operation.setdefault(
                            "x-hedron-htmx",
                            cast(JsonValue, dict(meta.htmx_inference)),
                        )
                    provenance = getattr(meta, "router_provenance", None)
                    if not provenance:
                        for route in app.routes:
                            if getattr(route, "operation_id", None) == op_id:
                                provenance = getattr(route, "hedron_provenance", None)
                                break
                    if provenance:
                        operation.setdefault("x-hedron-router-provenance", provenance)
                    descriptor = getattr(meta, "descriptor", None)
                    if descriptor is None:
                        handle = handle_map.get(meta.logical_id)
                        descriptor = getattr(handle, "descriptor", None)
                    if descriptor is None:
                        for handle in handle_map.values():
                            if getattr(handle, "path", None) == meta.path:
                                descriptor = getattr(handle, "descriptor", None)
                                break
                    if descriptor is None:
                        descriptor = descriptors.get(meta.logical_id)
                    if descriptor is None:
                        for item in descriptors.values():
                            if getattr(item, "path", None) == meta.path:
                                descriptor = item
                                break
                    if descriptor is not None:
                        from hedron_core.type_schema import type_schema_from_descriptor

                        loaded = type_schema_from_descriptor(descriptor)
                        if loaded is not None and loaded.schema_version >= 2:
                            operation.setdefault(
                                "x-hedron-input-schema",
                                cast(JsonValue, dict(loaded.input_projection)),
                            )
                            operation.setdefault(
                                "x-hedron-output-schema",
                                cast(JsonValue, dict(loaded.output_projection)),
                            )
                    scopes = getattr(meta, "requires_scopes", None)
                    endpoint = getattr(meta, "endpoint", None)
                    if scopes is None and endpoint is not None:
                        scopes = getattr(endpoint, "_hedron_requires_scopes", None)
                    if isinstance(scopes, RequiresScopes) and scopes.scopes:
                        operation.setdefault(
                            "security",
                            [{"hedronScopes": list(scopes.scopes)}],
                        )
                        needs_hedron_scopes = True
                    callbacks = getattr(meta, "openapi_callbacks", None)
                    if isinstance(callbacks, dict):
                        operation.setdefault("callbacks", cast(JsonValue, callbacks))
                    webhooks_note = getattr(meta, "openapi_webhooks", None)
                    if webhooks_note:
                        operation.setdefault("x-hedron-webhooks", webhooks_note)
                    responses = operation.setdefault("responses", cast(JsonValue, {}))
                    if not isinstance(responses, dict):
                        continue
                    ok = responses.setdefault("200", {})
                    if not isinstance(ok, dict):
                        continue
                    content = ok.setdefault("content", {})
                    if isinstance(content, dict):
                        content.setdefault("text/html", {"schema": {"type": "string"}})
        if needs_hedron_scopes:
            components = schema.setdefault("components", {})
            if isinstance(components, dict):
                schemes = components.setdefault("securitySchemes", {})
                if isinstance(schemes, dict):
                    schemes.setdefault(
                        "hedronScopes",
                        {
                            "type": "apiKey",
                            "in": "header",
                            "name": "X-Hedron-Scopes",
                            "description": (
                                "Declared application scopes. Hedron does not grant "
                                "access; the host application owns authorization."
                            ),
                        },
                    )
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi  # type: ignore[method-assign]
