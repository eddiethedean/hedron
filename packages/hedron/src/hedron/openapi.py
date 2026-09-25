"""OpenAPI post-processing for Hedron HTML routes."""

from __future__ import annotations

from contextlib import AbstractContextManager
from typing import cast

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from hedron.fastapi_compat import cached_openapi, set_cached_openapi
from hedron_core.registry import get_registry
from hedron_core.scopes import RequiresScopes
from hedron_core.typing_aliases import JsonObject, JsonValue
from hedron_core.typing_support import call_dynamic, dynamic_attribute
from hedron_core.updates import list_handle_descriptors

__all__ = ["install_openapi", "operation_id_for"]


def operation_id_for(kind: str, name: str, path: str, method: str) -> str:
    cleaned_path = path.strip("/").replace("/", "_").replace("{", "").replace("}", "") or "root"
    return f"hedron_{kind}_{name}_{method.lower()}_{cleaned_path}"


def install_openapi(app: FastAPI) -> None:
    def build_openapi() -> JsonObject:
        cached = cached_openapi(app)
        if cached is not None:
            return cast(JsonObject, cached)
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
        handles = dynamic_attribute(dynamic_attribute(app, "state"), "hedron_handles")
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
                    _ignored = operation.setdefault("x-hedron-kind", meta.kind)
                    _ignored = operation.setdefault("x-hedron-logical-id", meta.logical_id)
                    entry = None
                    catalog = dynamic_attribute(
                        dynamic_attribute(app, "state"), "hedron_interactions"
                    )
                    if catalog is not None:
                        getter = dynamic_attribute(catalog, "get")
                        if callable(getter):
                            entry = call_dynamic(getter, meta.logical_id)
                    if entry is not None:
                        descriptor_fingerprint = dynamic_attribute(entry, "descriptor_fingerprint")
                        _ignored = operation.setdefault(
                            "x-hedron-descriptor-fingerprint",
                            cast(JsonValue, descriptor_fingerprint),
                        )
                        type_schema_fingerprint = dynamic_attribute(
                            entry, "type_schema_fingerprint"
                        )
                        if type_schema_fingerprint:
                            _ignored = operation.setdefault(
                                "x-hedron-type-schema-fingerprint",
                                cast(JsonValue, type_schema_fingerprint),
                            )
                    if meta.htmx_inference:
                        _ignored = operation.setdefault(
                            "x-hedron-htmx",
                            cast(JsonValue, dict(meta.htmx_inference)),
                        )
                    provenance = dynamic_attribute(meta, "router_provenance")
                    if not provenance:
                        for route in app.routes:
                            if dynamic_attribute(route, "operation_id") == op_id:
                                provenance = dynamic_attribute(route, "hedron_provenance")
                                break
                    if provenance:
                        _ignored = operation.setdefault(
                            "x-hedron-router-provenance", cast(JsonValue, provenance)
                        )
                    descriptor = dynamic_attribute(meta, "descriptor")
                    if descriptor is None:
                        handle = handle_map.get(meta.logical_id)
                        descriptor = dynamic_attribute(handle, "descriptor")
                    if descriptor is None:
                        for handle in handle_map.values():
                            if dynamic_attribute(handle, "path") == meta.path:
                                descriptor = dynamic_attribute(handle, "descriptor")
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
                            _ignored = operation.setdefault(
                                "x-hedron-input-schema",
                                cast(JsonValue, dict(loaded.input_projection)),
                            )
                            _ignored = operation.setdefault(
                                "x-hedron-output-schema",
                                cast(JsonValue, dict(loaded.output_projection)),
                            )
                    scopes = dynamic_attribute(meta, "requires_scopes")
                    endpoint = dynamic_attribute(meta, "endpoint")
                    if scopes is None and endpoint is not None:
                        scopes = dynamic_attribute(endpoint, "_hedron_requires_scopes")
                    if isinstance(scopes, RequiresScopes) and scopes.scopes:
                        _ignored = operation.setdefault(
                            "security",
                            [{"hedronScopes": list(scopes.scopes)}],
                        )
                        needs_hedron_scopes = True
                    callbacks = dynamic_attribute(meta, "openapi_callbacks")
                    if isinstance(callbacks, dict):
                        _ignored = operation.setdefault("callbacks", cast(JsonValue, callbacks))
                    webhooks_note = dynamic_attribute(meta, "openapi_webhooks")
                    if webhooks_note:
                        _ignored = operation.setdefault(
                            "x-hedron-webhooks", cast(JsonValue, webhooks_note)
                        )
                    responses = operation.setdefault("responses", cast(JsonValue, {}))
                    if not isinstance(responses, dict):
                        continue
                    ok = responses.setdefault("200", {})
                    if not isinstance(ok, dict):
                        continue
                    content = ok.setdefault("content", {})
                    if isinstance(content, dict):
                        _ignored = content.setdefault("text/html", {"schema": {"type": "string"}})
        if needs_hedron_scopes:
            components = schema.setdefault("components", {})
            if isinstance(components, dict):
                schemes = components.setdefault("securitySchemes", {})
                if isinstance(schemes, dict):
                    _ignored = schemes.setdefault(
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
        set_cached_openapi(app, schema)
        return schema

    def custom_openapi() -> JsonObject:
        runtime = getattr(app, "_hedron_runtime", None)
        activate = getattr(runtime, "activate", None)
        if callable(activate):
            with cast(AbstractContextManager[object], activate()):
                return build_openapi()
        return build_openapi()

    app.openapi = custom_openapi  # type: ignore[method-assign]
